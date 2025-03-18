
# # -*- coding: utf-8  -*-
# import pywikibot
# """
# To get the sitelink of a specific wiki. Use "item.getSitelink('INSERT DBNAME')"
# """

# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# item.getSitelink('enwiki')

# #Result in: 'Douglas Adams'

# -*- coding: utf-8  -*-
import pywikibot

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()
item = pywikibot.ItemPage(repo, "Q238723")

sitedict = {'site':'enwiki', 'title':'Douglas Adams'}

item.setSitelink(sitedict, summary=u'Setting (/updating?) sitelink.')

