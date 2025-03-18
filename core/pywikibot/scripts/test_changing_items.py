import pywikibot
from pywikibot import pagegenerators as pg

site = pywikibot.Site("test", "wikidata") #changed wikidata to test for safety
repo = site.data_repository()
property = "P462"
error_dict = {"Q13191": "Q39338",      #orange - "fruit": "color"
              "Q897": "Q208045",       #gold - "element": "color"
              "Q753": "Q2722041",      #copper - "element": "color"
              "Q25381": "Q679355",     #amber - "material": "color"
              "Q134862": "Q5069879",   #champagne - "drink": "color"
              "Q1090": "Q317802",      #silver - "element": "color"
              "Q1173": "Q797446",      #burgundy - "region": "color
              "Q13411121": "Q5148721", #peach - "fruit": "color"
              }

def correct_claim(generator, key):
    for page in generator:
        item_dict = page.get()
        claim_list = item_dict["claims"][property]
        for claim in claim_list:
            trgt = claim.getTarget()
            if trgt.id == key:
                print("Correcting {} to {}".format(key, error_dict[key]))
                correct_page = pywikibot.ItemPage(repo, error_dict[key], 0)
                claim.changeTarget(correct_page)

for key in error_dict:
    wdq = 'SELECT DISTINCT ?item WHERE {{ ?item p:{0} ?statement0. ?statement0 (ps:{0}) wd:{1}. }} LIMIT 5'.format(property, key)
    generator = pg.WikidataSPARQLPageGenerator(wdq, site=site)
    correct_claim(generator, key)
