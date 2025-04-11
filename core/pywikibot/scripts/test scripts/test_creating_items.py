import pywikibot
site = pywikibot.Site("test", "wikidata")

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Testing item creation. Labels added.")     # Add description here or in another function
    return new_item.getID()

some_labels = {"en": "MalletHoatzintesting24562", "de": "MalletHoatzintesting24562"}
new_item_id = create_item(site, some_labels)

print(f"New item created with ID: {new_item_id}")

