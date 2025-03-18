from collections import OrderedDict
import pywikibot
import csv


site = pywikibot.Site("en", "wikipedia")
page = pywikibot.Page(site, "Douglas Adams")
item = pywikibot.ItemPage.fromPage(page)

item_dict = item.get()
lbl_dict = item_dict["labels"]
lbl_sdict = OrderedDict(sorted(lbl_dict.items())) #Sorting the dictionary

with open("output_douglas.csv", "w", newline="", encoding='utf-16') as csvf:
    fields = ["lang-code", "label"]
    writer = csv.DictWriter(csvf, fieldnames=fields)
    writer.writeheader()
    for key in lbl_sdict:
        writer.writerow({"lang-code": key, "label": lbl_sdict[key]})