import pywikibot
from pywikibot.data import api
import pandas as pd
import re
import os
import sys
from datetime import datetime, timedelta
import time
import logging

# -------------------------
# Logging Setup
# -------------------------

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to the pywiki root
pywiki_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

# Define the logs directory path
logs_dir = os.path.join(pywiki_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Log file name with timestamp
log_filename = os.path.join(logs_dir, f"wikidata_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# -------------------------
# Lock file time-out
# -------------------------
LOCK_FILE = "last_run.lock"

def is_recently_run(min_minutes=5):
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            try:
                last_run = datetime.fromisoformat(f.read().strip())
                if datetime.now() - last_run < timedelta(minutes=min_minutes):
                    return True
            except Exception:
                pass
    return False

def update_last_run():
    with open(LOCK_FILE, "w") as f:
        f.write(datetime.now().isoformat())

# -------------------------
# Property map
# -------------------------
property_map = {
    "P50": {"property": "P50", "type": "string"},
    "P767": {"property": "P767", "type": "string"},
    "P761": {"property": "P761", "type": "date"},
    "P145": {"property": "P145", "type": "item"},
    "P31": {"property": "P31", "type": "string"},
    "P31_2": {"property": "P31", "type": "string"},
    "P82": {"property": "P82", "type": "item"}
}

# -------------------------
# Source map
# -------------------------
source_map = {
    "P149": {"property": "P149", "type": "item", "targets": ["P82"]},
}

# -------------------------
# Read CSV and clean headers
# -------------------------
def read_csv_to_df(path):
    df = pd.read_csv(path)
    df.columns = [col.split()[0] if "(" in col else col for col in df.columns]
    col_counts = {}
    new_cols = []
    for col in df.columns:
        if col not in col_counts:
            col_counts[col] = 1
            new_cols.append(col)
        else:
            col_counts[col] += 1
            new_cols.append(f"{col}_{col_counts[col]}")
    df.columns = new_cols

    if "QID" in df.columns:
        df["QID"] = df["QID"].astype(str)

    return df

# -------------------------
# Wikidata API helpers
# -------------------------
def get_items(site, item_title):
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": item_title
    }
    request = api.Request(site=site, parameters=params)
    return request.submit()

def check_item_exists(site, item_title):
    search_results = get_items(site, item_title)
    if "search" in search_results and len(search_results["search"]) > 0:
        return search_results["search"][0]["id"]
    return None

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Creating a new item.")
    return new_item.getID()

def wait_for_item_to_be_searchable(site, label, max_wait=600, interval=60):
    waited = 0
    while waited < max_wait:
        found_id = check_item_exists(site, label)
        if found_id:
            logging.info(f"Item '{label}' is now indexed as {found_id}. Continuing...")
            return True
        logging.info(f"Item '{label}' not yet indexed. Waiting {interval}s...")
        time.sleep(interval)
        waited += interval
    logging.warning(f"Timeout: Item '{label}' still not indexed after {max_wait} seconds.")
    return False

def check_and_create_item(site, item_title):
    item_id = check_item_exists(site, item_title)
    if item_id:
        logging.info(f"Skipping title '{item_title}' — item already exists as {item_id}, but no QID in CSV.")
        return None
    else:
        logging.info(f"Creating new item for: {item_title}")
        labels = {"en": item_title}
        new_id = create_item(site, labels)
        wait_for_item_to_be_searchable(site, item_title)
        return new_id

def claim_already_exists(item, prop, target_value):
    existing_claims = item.claims.get(prop, [])
    for claim in existing_claims:
        if isinstance(target_value, pywikibot.ItemPage) and claim.getTarget().id == target_value.id:
            return True
        elif isinstance(target_value, str) and claim.getTarget() == target_value:
            return True
        elif isinstance(target_value, pywikibot.WbTime) and claim.getTarget().toTimestr() == target_value.toTimestr():
            return True
    return False

def set_descriptions(site, item_id, row):
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get(force=True)

    new_descriptions = {}
    for col in row.index:
        match = re.match(r"[Dd]escription_(\w+)", col)
        if match:
            lang = match.group(1)
            new_desc = str(row[col]).strip()
            if pd.notna(new_desc) and new_desc:
                current_desc = item.descriptions.get(lang, "")
                if new_desc != current_desc:
                    new_descriptions[lang] = new_desc

    if new_descriptions:
        try:
            item.editDescriptions(new_descriptions, summary="Setting/updating item descriptions.")
            logging.info(f"Descriptions updated for {item_id}: {new_descriptions}")
        except Exception as e:
            logging.error(f"Failed to set descriptions for {item_id}: {e}")
    else:
        logging.info(f"No description changes needed for {item_id}.")

def source_bundle_exists(existing_sources, new_sources):
    for existing in existing_sources:
        match_count = 0
        for new in new_sources:
            prop = new.getID()
            if prop not in existing:
                break
            found = False
            for existing_claim in existing[prop]:
                if new.getTarget() == existing_claim.getTarget():
                    found = True
                    break
            if found:
                match_count += 1
        if match_count == len(new_sources):
            return True
    return False

def add_claims(site, item_id, row, property_map):
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    for col in row.index:
        if col in ["Title", "QID"] or col not in property_map or pd.isna(row[col]):
            continue

        mapping = property_map[col]
        prop = mapping["property"]
        val_type = mapping["type"]
        value = row[col]

        try:
            if val_type == "item":
                match = re.search(r"Q\d+", str(value))
                if match:
                    target = pywikibot.ItemPage(repo, match.group(0))
                    target.get()

                    if claim_already_exists(item, prop, target):
                        logging.info(f"Claim {prop} -> {target.id} already exists. Skipping.")
                        continue

                    claim = pywikibot.Claim(repo, prop)
                    claim.setTarget(target)
                    item.addClaim(claim, summary=f"Adding item claim {prop} -> {target.id}")
                else:
                    logging.warning(f"Skipping {col}: No QID in value '{value}'")

            elif val_type == "string":
                if claim_already_exists(item, prop, str(value)):
                    logging.info(f"Claim {prop} -> '{value}' already exists. Skipping.")
                    continue

                claim = pywikibot.Claim(repo, prop)
                claim.setTarget(str(value))
                item.addClaim(claim, summary=f"Adding string claim {prop} -> {value}")

            elif val_type == "date":
                parsed = pd.to_datetime(value, errors="coerce")
                if pd.notna(parsed):
                    date_target = pywikibot.WbTime(
                        year=parsed.year, month=parsed.month, day=parsed.day
                    )

                    if claim_already_exists(item, prop, date_target):
                        logging.info(f"Date claim {prop} -> {parsed.date()} already exists. Skipping.")
                        continue

                    dateclaim = pywikibot.Claim(repo, prop)
                    dateclaim.setTarget(date_target)
                    item.addClaim(dateclaim, summary=f"Adding date claim {prop} -> {parsed.date()}")
                else:
                    logging.warning(f"Invalid date for {prop}: {value}")

        except Exception as e:
            logging.error(f"Error on {col} ({prop}): {e}")

    logging.info(f"Finished processing claims for {item_id}")

def add_sources(site, item_id, row, source_map):
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    for prop, claims in item.claims.items():
        for claim in claims:
            try:
                existing_sources = claim.getSources()
            except Exception as e:
                logging.warning(f"Could not get sources for claim {claim}: {e}")
                continue

            new_sources = []

            for source_col, source_info in source_map.items():
                target_props = source_info.get("targets")
                if target_props and prop not in target_props:
                    continue

                source_prop = source_info["property"]
                source_type = source_info["type"]
                source_value = row[source_col]

                if pd.isna(source_value):
                    continue

                try:
                    source_claim = pywikibot.Claim(repo, source_prop, is_reference=True)

                    if source_type == "item":
                        match = re.search(r"Q\d+", str(source_value))
                        if match:
                            target = pywikibot.ItemPage(repo, match.group(0))
                            target.get()
                            source_claim.setTarget(target)
                        else:
                            logging.warning(f"Invalid Q-ID for source in column {source_col}: {source_value}")
                            continue
                    elif source_type == "string":
                        source_claim.setTarget(str(source_value))
                    elif source_type == "date":
                        dt = pd.to_datetime(source_value, errors="coerce")
                        if pd.isna(dt):
                            logging.warning(f"Invalid date for source in column {source_col}: {source_value}")
                            continue
                        date_target = pywikibot.WbTime(year=dt.year, month=dt.month, day=dt.day)
                        source_claim.setTarget(date_target)
                    else:
                        logging.warning(f"Unsupported source type '{source_type}' for {source_prop}")
                        continue

                    new_sources.append(source_claim)

                except Exception as e:
                    logging.error(f"Error building source claim for {source_col}: {e}")

            if new_sources:
                if source_bundle_exists(existing_sources, new_sources):
                    logging.info(f"Source(s) already exist for claim {claim.getID()} on {item_id}. Skipping.")
                    continue
                try:
                    claim.addSources(new_sources, summary="Adding source(s) to claim.")
                    logging.info(f"Added sources to claim {claim.getID()} on {item_id}")
                except Exception as e:
                    logging.error(f"Failed to add sources to claim {claim.getID()}: {e}")

def process_csv_and_create_items(df, site, property_map, source_map):
    for idx, row in df.iterrows():
        qid = str(row.get("QID")).strip() if "QID" in row else None

        if not qid or not re.match(r"^Q\d+$", qid):
            title = row["Title"]
            qid = check_and_create_item(site, title)

            if not qid:
                logging.warning(f"Skipping '{title}' — no QID available.")
                continue

            df.at[idx, "QID"] = qid
            df.to_csv("test_data3.csv", index=False)

        add_claims(site, qid, row, property_map)
        set_descriptions(site, qid, row)
        add_sources(site, qid, row, source_map)

if __name__ == "__main__":
    if is_recently_run(min_minutes=0):
        logging.warning("Script ran recently. Please wait 5 minutes before running it again.")
        sys.exit(1)

    update_last_run()
    df = read_csv_to_df("test_data3.csv")
    site = pywikibot.Site("test", "wikidata")
    process_csv_and_create_items(df, site, property_map, source_map)
    logging.info("Script completed successfully.")
