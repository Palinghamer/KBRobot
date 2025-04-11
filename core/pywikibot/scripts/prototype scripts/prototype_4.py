import pywikibot
from pywikibot.data import api
import pandas as pd
import re
import os
import sys
from datetime import datetime, timedelta
import time


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
    "P50": {"property": "P50", "type": "string"},             # author (string)
    "P767": {"property": "P767", "type": "string"},           # contributors (string)
    "P761": {"property": "P761", "type": "date"},             # publication date (date)
    "P145": {"property": "P145", "type": "item"},             # publisher (item)
    "P31": {"property": "P31", "type": "string"},             # URL to item class (string)
    "P31_2": {"property": "P31", "type": "string"},           
    "P82": {"property": "P82", "type": "item"}                # instance of (item)
}

# -------------------------
# Source map
# -------------------------
source_map = {
    "P149": {"property": "P149", "type": "item", "targets": ["P82"]},  # add LabEL as source to instance of
}

# -------------------------
# Read CSV and clean headers
# -------------------------
def read_csv_to_df(path):
    df = pd.read_csv(path)
    df.columns = [col.split()[0] if "(" in col else col for col in df.columns]  # Strip labels
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

import time  # make sure this is imported at the top

def wait_for_item_to_be_searchable(site, label, max_wait=600, interval=60):
    """
    Wait for a newly created item to appear in the wbsearchentities index.
    max_wait: total time to wait in seconds
    interval: how often to retry
    """
    waited = 0
    while waited < max_wait:
        found_id = check_item_exists(site, label)
        if found_id:
            print(f"Item '{label}' is now indexed as {found_id}. Continuing...")
            return True
        print(f"Item '{label}' not yet indexed. Waiting {interval}s...")
        time.sleep(interval)
        waited += interval
    print(f"Timeout: Item '{label}' still not indexed after {max_wait} seconds.")
    return False


def check_and_create_item(site, item_title):
    item_id = check_item_exists(site, item_title)
    if item_id:
        print(f"Skipping title '{item_title}' — item already exists as {item_id}, but no QID in CSV.")
        return None
    else:
        print(f"Creating new item for: {item_title}")
        labels = {"en": item_title}
        new_id = create_item(site, labels)

        # Wait until it's indexed
        wait_for_item_to_be_searchable(site, item_title)
        return new_id

def claim_already_exists(item, prop, target_value):
    """
    Checks whether a claim with the given property and target already exists.
    """
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
    """
    Sets descriptions for a given item based on the row data.
    Only updates if the description differs from what's already on Wikidata.
    """
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get(force=True)  # Ensure fresh data

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
            print(f"Descriptions updated for {item_id}: {new_descriptions}")
        except Exception as e:
            print(f"Failed to set descriptions for {item_id}: {e}")
    else:
        print(f"No description changes needed for {item_id}.")

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

# -------------------------
# Add claims to item
# -------------------------
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
                        print(f"Claim {prop} -> {target.id} already exists. Skipping.")
                        continue

                    claim = pywikibot.Claim(repo, prop)
                    claim.setTarget(target)
                    item.addClaim(claim, summary=f"Adding item claim {prop} -> {target.id}")
                else:
                    print(f"Skipping {col}: No QID in value '{value}'")

            elif val_type == "string":
                if claim_already_exists(item, prop, str(value)):
                    print(f"Claim {prop} -> '{value}' already exists. Skipping.")
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
                        print(f"Date claim {prop} -> {parsed.date()} already exists. Skipping.")
                        continue

                    dateclaim = pywikibot.Claim(repo, prop)
                    dateclaim.setTarget(date_target)
                    item.addClaim(dateclaim, summary=f"Adding date claim {prop} -> {parsed.date()}")
                else:
                    print(f"Invalid date for {prop}: {value}")

        except Exception as e:
            print(f"Error on {col} ({prop}): {e}")

    print(f"Finished processing claims for {item_id}\n")

# -------------------------
# Add sources to claims
# -------------------------
def add_sources(site, item_id, row, source_map):
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    for prop, claims in item.claims.items():
        for claim in claims:
            try:
                existing_sources = claim.getSources()
            except Exception as e:
                print(f"Could not get sources for claim {claim}: {e}")
                continue

            new_sources = []
            already_present = False

            for source_col, source_info in source_map.items():
                target_props = source_info.get("targets")
                if target_props and prop not in target_props:
                    continue

                source_prop = source_info["property"]
                source_type = source_info["type"]
                source_value = row[source_col]

                if pd.isna(source_value):
                    continue

                for src in existing_sources:
                    if source_prop in src:
                        for s in src[source_prop]:
                            try:
                                if source_type == "item" and isinstance(s.getTarget(), pywikibot.ItemPage):
                                    if s.getTarget().id == source_value:
                                        already_present = True
                                elif source_type == "string" and s.getTarget() == str(source_value):
                                    already_present = True
                                elif source_type == "date" and isinstance(s.getTarget(), pywikibot.WbTime):
                                    dt = pd.to_datetime(source_value, errors="coerce")
                                    if dt and s.getTarget().toTimestr() == pywikibot.WbTime(
                                        year=dt.year, month=dt.month, day=dt.day
                                    ).toTimestr():
                                        already_present = True
                            except Exception:
                                continue

                if already_present:
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
                            print(f"Invalid Q-ID for source in column {source_col}: {source_value}")
                            continue
                    elif source_type == "string":
                        source_claim.setTarget(str(source_value))
                    elif source_type == "date":
                        dt = pd.to_datetime(source_value, errors="coerce")
                        if pd.isna(dt):
                            print(f"Invalid date for source in column {source_col}: {source_value}")
                            continue
                        date_target = pywikibot.WbTime(year=dt.year, month=dt.month, day=dt.day)
                        source_claim.setTarget(date_target)
                    else:
                        print(f"Unsupported source type '{source_type}' for {source_prop}")
                        continue

                    new_sources.append(source_claim)

                except Exception as e:
                    print(f"Error building source claim for {source_col}: {e}")
                    
            if new_sources:
                if source_bundle_exists(existing_sources, new_sources):
                    print(f"Source(s) already exist for claim {claim.getID()} on {item_id}. Skipping.")
                    continue
                try:
                    claim.addSources(new_sources, summary="Adding source(s) to claim.")
                    print(f"Added sources to claim {claim.getID()} on {item_id}")
                except Exception as e:
                    print(f"Failed to add sources to claim {claim.getID()}: {e}")

# -------------------------
# Main loop
# -------------------------
def process_csv_and_create_items(df, site, property_map, source_map):
    for idx, row in df.iterrows():
        qid = str(row.get("QID")).strip() if "QID" in row else None

        if not qid or not re.match(r"^Q\d+$", qid):
            title = row["Title"]
            qid = check_and_create_item(site, title)

            if not qid:
                print(f"Skipping '{title}' — no QID available.")
                continue

            df.at[idx, "QID"] = qid
            df.to_csv("test_data3.csv", index=False)  # <-- immediately save

        add_claims(site, qid, row, property_map)
        set_descriptions(site, qid, row)
        add_sources(site, qid, row, source_map)


# -------------------------
# Running
# -------------------------
if __name__ == "__main__":
    if is_recently_run(min_minutes=1):
        print("Script ran recently. Please wait 5 minutes before running it again.")
        sys.exit(1)

    update_last_run()

    df = read_csv_to_df("test_data3.csv")
    site = pywikibot.Site("test", "wikidata")
    process_csv_and_create_items(df, site, property_map, source_map)