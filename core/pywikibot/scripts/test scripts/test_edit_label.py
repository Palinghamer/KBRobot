#-----------------To make simple edits with manual descriptions------

# import pywikibot

# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# new_labels = {"en": "MalletHoatzinBot test"}
# new_descr = {"en": "This serves as an environment for live testing the MalletHoatzinBot. Please be gentle with it."}
# new_alias = {"en": ["MalletHoatzinBot Sandbox"]}
# item.editLabels(labels=new_labels, summary="Setting new labels.")
# item.editDescriptions(new_descr, summary="Setting new descriptions.")
# item.editAliases(new_alias, summary="Setting new aliases.")

#-----------------To make separate edits with automated descriptions------

import pywikibot

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()
item = pywikibot.ItemPage(repo, "Q238723")

new_labels = {"en": "MalletHoatzinBot Sandbox", "de": "MalletHoatzinBot Sandkasten"}
new_descr = {"en": "This serves as an environment for live testing the MalletHoatzinBot. Please be gentle with it.",
             "de": "Dies dient als Umgebung für den Live-Test des MalletHoatzinBot. Bitte gehen Sie sanft mit ihm um."}
new_alias = {"en": ["MalletHoatzinBot test", "MalletHoatzinBot Playground"],
             "de": ["MalletHoatzinBot test", "MalletHoatzinBot Spielplatz"]}

for key in new_labels:
    item.editLabels(labels={key: new_labels[key]},
        summary="Setting label: {} = '{}'".format(key, new_labels[key]))

for key in new_descr:
    item.editDescriptions({key: new_descr[key]},
        summary="Setting description: {} = '{}'".format(key, new_descr[key]))

for key in new_alias:
    item.editAliases({key: new_alias[key]},
        summary="Settings aliases: {} = '{}'".format(key, new_alias[key]))
    
#-----------------To make separate edits with automated descriptions------

# import pywikibot

# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# data = {"labels": {"en": "bear", "de": "Bär"},
#   "descriptions": {"en": "gentle creature of the forest", "de": "Friedlicher Waldbewohner"},
#        "aliases": {"en": ["brown bear", "grizzly bear", "polar bear"], "de": ["Braunbär", "Grizzlybär", "Eisbär"]},
#      "sitelinks": [{"site": "enwiki", "title": "Bear"}, {"site": "dewiki", "title": "Bär"}]}
# item.editEntity(data, summary=u'Edited item: set labels, descriptions, aliases')
