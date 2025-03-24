import pywikibot
from pywikibot.data import api
import pandas as pd
import re

# -------------------------
# Property map for this example
# -------------------------
property_map = {
    "P50": {"property": "P50", "type": "string"},             # author (string)
    "P767": {"property": "P767", "type": "string"},           # contributors (string)
    "P761": {"property": "P761", "type": "date"},             # publication date
    "P145": {"property": "P145", "type": "item"},             # publisher (Q-ID expected)
    "P31": {"property": "P31", "type": "string"},             # URL to item class (string for demo)
    "P31_2": {"property": "P31", "type": "string"},           # another P31
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
def add_claims(site, item_title, row, property_map):
    repo = site.data_repository()
    item_id = check_item_exists(site, item_title)
    if not item_id:
        print(f"Item '{item_title}' does not exist. Cannot add claims.")
        return

    item = pywikibot.ItemPage(repo, item_id)
    item.get()

    for col in row.index:
        if col == "Title" or col not in property_map or pd.isna(row[col]):
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

    print(f"Claims added for {item_title}\n")


# -------------------------
# Main loop
# -------------------------
def process_csv_and_create_items(df, site, property_map):
    for _, row in df.iterrows():
        title = row["Title"]
        check_and_create_item(site, title)
        add_claims(site, title, row, property_map)

# -------------------------
# Run the script
# -------------------------
if __name__ == "__main__":
    df = read_csv_to_df("test_data.csv")
    site = pywikibot.Site("test", "wikidata")
    process_csv_and_create_items(df, site, property_map)
