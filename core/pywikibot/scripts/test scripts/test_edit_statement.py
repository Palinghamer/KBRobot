# Using addClaim() to add a claim uing a property and a target item--------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Adds claim to item
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# claim = pywikibot.Claim(repo, u'P82') #Adding 'instance of '(P31)
# target = pywikibot.ItemPage(repo, u"Q300") #Connecting P31 with sandbox (Q300)
# claim.setTarget(target) #Set the target value in the local object.

# item.addClaim(claim, summary=u'Adding claim to Q238723') #Inserting value with summary to Q238723

#Stating strings and coordinates---------------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Adding claims with string (IMDb ID (P345) and coordinate (coordinate location (P625)) datatypes (URL is the same as string)
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, u"Q238723")

# stringclaim = pywikibot.Claim(repo, u'P7711') #Adding described at URL (P7711)
# stringclaim.setTarget(u"https://test.wikidata.org/wiki/Q238723") #Using a string
# item.addClaim(stringclaim, summary=u'Adding string claim')

# coordinateclaim  = pywikibot.Claim(repo, u'P125') #Adding coordinate location (P125)
# coordinate = pywikibot.Coordinate(lat=52.208, lon=0.1225, precision=0.001, site=site) #With location markes
# coordinateclaim.setTarget(coordinate)
# item.addClaim(coordinateclaim, summary=u'Adding coordinate claim')

#Single value string & check if exists------------------------
# # -*- coding: utf-8  -*-
# import pywikibot
# """
# First check if P7711 already exists for Q238723. If not add claim P7711 with the string 'https://test.wikidata.org/wiki/Q238723'.
# This works for claims that only allow a single value.
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, u"Q238723") #
# claims = item.get(u'claims') #Get all the existing claims

# if u'P7711' in claims[u'claims']: #described at URL (P7711) only allow single values. So if a value is presented already, print error.
#     pywikibot.output(u'Error: Already have a Described at URL value!')
# else:
#     stringclaim = pywikibot.Claim(repo, u'P7711') #Else, add the value
#     stringclaim.setTarget('https://test.wikidata.org/wiki/Q238723')
#     item.addClaim(stringclaim, summary=u'Adding a Described at URL')

#Setting Time/Date ---------------------------
#-*- coding: utf-8  -*-
import pywikibot
"""
Adding value for data type: Point in time.
"""
site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()
item = pywikibot.ItemPage(repo, u"Q238723")

dateclaim = pywikibot.Claim(repo, u'P95197')
dateOfBirth = pywikibot.WbTime(year=2025, month=3, day=10)
dateclaim.setTarget(dateOfBirth)
item.addClaim(dateclaim, summary=u'Adding dateOfBirth')


#Deleting statements ------------------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Remove all claims of P95197
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, u"Q238723")
# item.get() #To access item.claims

# for claim in item.claims['P95197']: #Iterate over every statement of P95197
#     item.removeClaims(claim, summary=u'Removing dateOfBirth') #Removing claim

#Removing only the first claim--------------------

# -*- coding: utf-8  -*-
# import pywikibot
# """
# Remove the first claim of P82
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, u"Q238723")
# item.get() #To access item.claims

# if 'P82' in item.claims and item.claims['P82']:
#         item.removeClaims(item.claims['P82'][0])
