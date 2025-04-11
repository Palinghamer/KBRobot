import pywikibot
site = pywikibot.Site("en", "wikipedia")
page = pywikibot.Page(site, "Douglas Adams")
item = pywikibot.ItemPage.fromPage(page)

#Can also access the site directly: 
#site = pywikibot.Site("wikidata", "wikidata")
#repo = site.data_repository()
#item = pywikibot.ItemPage(repo, "Q42")

#print(item)     #prints [[wikidata:Q42]]
#print(dir(item))      #prints entire directory
#print(item.exists())      #prints boolean

# item_dict = item.get()   #get() turns the item into a dictionary 
#print(item_dict.keys())

#print(item_dict["labels"])
#print(item_dict["aliases"])

