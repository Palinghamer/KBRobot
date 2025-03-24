import pywikibot
from pywikibot.data import api
import pandas as pd
import re

# -------------------------
# Property map
# -------------------------
property_map = {
    "P50": {"property": "P50", "type": "string"},             # author (string)
    "P767": {"property": "P767", "type": "string"},           # contributors (string)
    "P761": {"property": "P761", "type": "date"},             # publication date
    "P145": {"property": "P145", "type": "item"},             # publisher (Q-ID expected)
    "P31": {"property": "P31", "type": "string"},             # URL to item class (string for demo)
    "P31_2": {"property": "P31", "type": "string"},           
    "P82": {"property": "P82", "type": "item"}                # instance of (item for type of work)
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

    # 👇 Fix for FutureWarning: force Wikidata_ID to be string
    if "Wikidata_ID" in df.columns:
        df["Wikidata_ID"] = df["Wikidata_ID"].astype(str)
    
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

def check_and_create_item(site, item_title):
    item_id = check_item_exists(site, item_title)
    if item_id:
        print(f"Item '{item_title}' exists: {item_id}")
        return item_id
    else:
        print(f"Creating new item for: {item_title}")
        labels = {"en": item_title}
        return create_item(site, labels)

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

# -------------------------
# Add claims to item
# -------------------------
def add_claims(site, item_id, row, property_map):
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    for col in row.index:
        if col in ["Title", "Wikidata_ID"] or col not in property_map or pd.isna(row[col]):
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

            if new_sources and not already_present:
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
        qid = str(row.get("Wikidata_ID")).strip() if "Wikidata_ID" in row else None

        if not qid or not re.match(r"^Q\d+$", qid):
            title = row["Title"]
            qid = check_and_create_item(site, title)
            df.at[idx, "Wikidata_ID"] = qid  # Save QID back into the DataFrame

        add_claims(site, qid, row, property_map)
        add_sources(site, qid, row, source_map)
    
    # Optional: save updated file with QIDs
    df.to_csv("test_data3.csv", index=False)

# -------------------------
# Running
# -------------------------
if __name__ == "__main__":
    df = read_csv_to_df("test_data3.csv")
    site = pywikibot.Site("test", "wikidata")
process_csv_and_create_items(df, site, property_map, source_map) 
