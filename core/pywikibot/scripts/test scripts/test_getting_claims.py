import pywikibot
import json

#Get the item
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
item = pywikibot.ItemPage(repo, "Q2225")

item_dict = item.get() #Get the item dictionary
clm_dict = item_dict["claims"] # Get the claim dictionary
#print(clm_dict)
clm_list = clm_dict["P2069"]

# for clm in clm_list: #To print all claims about P2069
#     print(clm)


# # for clm in clm_list:
# #     print(clm)

# # for clm in clm_list:
# #     print(clm.toJSON())

# for clm in clm_list:
#     ...
#     clm_trgt = clm.getTarget()
#     print(clm_trgt)
#     print(type(clm_trgt))
#     print(dir(clm_trgt))

for clm in clm_list:
    clm_trgt = clm.getTarget()
    print(clm_trgt.amount)
    print(clm_trgt.unit)

