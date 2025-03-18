import pywikibot
import json

site = pywikibot.Site("en", "wikipedia")
page = pywikibot.Page(site, "Douglas Adams")
item = pywikibot.ItemPage.fromPage(page)

item_dict = item.get()
lbl_dict = item_dict["labels"]

with open("output_douglas.json", "w", newline="", encoding='utf-16') as jsonf:
    json.dump(lbl_dict.__dict__, jsonf, ensure_ascii=False, sort_keys=True, indent=4)