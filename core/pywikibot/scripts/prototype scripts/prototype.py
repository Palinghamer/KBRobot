import pywikibot
from pywikibot.data import api
import pandas as pd
import re

# ----------------------------------------
# Read CSV into DataFrame
# ----------------------------------------

def read_csv_to_df(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

df = read_csv_to_df("test3.csv")

# ----------------------------------------
# Set up Wikidata test connection
# ----------------------------------------

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()

# ----------------------------------------
# API helpers
# ----------------------------------------

def get_items(site, item_title):
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": item_title
    }
    request = api.Request(site=site, parameters=params)
    response = request.submit()
    return response

def check_item_exists(site, item_title):
    search_results = get_items(site, item_title)
    if "search" in search_results and len(search_results["search"]) > 0:
        return search_results["search"][0]["id"]
    return None

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Creating a new item with specified labels.")
    return new_item.getID()

def check_and_create_item(site, item_title):
    item_id = check_item_exists(site, item_title)
    if item_id:
        print(f"Item with title '{item_title}' already exists with ID: {item_id}")
    else:
        print(f"Item with title '{item_title}' does not exist. Creating a new item...")
        labels = {"en": item_title}
        item_id = create_item(site, labels)
        print(f"New item created with ID: {item_id}")
    return item_id

# ----------------------------------------
# Claim helpers
# ----------------------------------------

def extract_property_id(header):
    match = re.search(r'(P\d+)', header)
    return match.group(1) if match else None

def clean_qid(value):
    match = re.match(r'^(Q\d+)', value)
    return match.group(1) if match else None

def add_claim(item, prop, value):
    try:
        claim = pywikibot.Claim(repo, prop)

        # Handle date
        if prop == "P577" and re.match(r'\d{2}/\d{2}/\d{2,4}', value):
            day, month, year = map(int, value.split('/'))
            if year < 100:
                year += 2000
            target = pywikibot.WbTime(year=year, month=month, day=day)

        # Handle URL
        elif value.startswith("http"):
            target = value  # URLs are added as string targets

        # Handle QID
        elif clean_qid(value):
            qid = clean_qid(value)
            target = pywikibot.ItemPage(repo, qid)

        # Fallback: plain string
        else:
            target = value

        claim.setTarget(target)
        item.addClaim(claim, summary=f"Adding {prop} claim from CSV")
        print(f"✓ Added {prop} → {value}")

    except Exception as e:
        print(f"⚠️ Error adding claim {prop} → {value}: {e}")

# ----------------------------------------
# Main logic
# ----------------------------------------

def process_dataframe(df):
    for idx, row in df.iterrows():
        title = row['Title']
        item_id = check_and_create_item(site, title)
        item = pywikibot.ItemPage(repo, item_id)
        item.get()

        for col in df.columns:
            if col == "Title":
                continue
            prop = extract_property_id(col)
            if not prop:
                continue

            value = row[col]
            if pd.isna(value) or str(value).strip() == "":
                continue

            # Allow semicolon-separated multiple values
            values = [v.strip() for v in str(value).split(';')]
            for val in values:
                add_claim(item, prop, val)

# ----------------------------------------
# Run it!
# ----------------------------------------

process_dataframe(df)
