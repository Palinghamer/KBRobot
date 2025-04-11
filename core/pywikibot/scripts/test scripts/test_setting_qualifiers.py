# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Adding a qualifier to newly-created claim/statement
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# #CLAIM
# claim = pywikibot.Claim(repo, u'P769') #Adding located in the administrative territorial entity (P769)
# target = pywikibot.ItemPage(repo, u"Q519") #Connecting P131 with Cambridge (Q519)
# claim.setTarget(target) #Set the target value in the local object.
# item.addClaim(claim, summary=u'Adding claim to Q238723') #Inserting value with summary to Q210194

# #QUALIFIER
# qualifier = pywikibot.Claim(repo, u'P100')
# target = pywikibot.ItemPage(repo, "Q35409")
# qualifier.setTarget(target)
# claim.addQualifier(qualifier, summary=u'Adding a qualifier.')

#Adding qualifier ------------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Adding a qualifier to existing claims/statements
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")
# item.get() #Fetch all page data, and cache it.

# for claim in item.claims['P769']: #Finds all statements (P131)
#     if 'P100' not in claim.qualifiers: #If not already exist

#         # Generate QUALIFIER FOR EXISTENCE STATEMENTS/CLAIMS
#         qualifier = pywikibot.Claim(repo, u'P100')
#         target = pywikibot.ItemPage(repo, "Q35409")
#         qualifier.setTarget(target)

#         claim.addQualifier(qualifier, summary=u'Adding a qualifier.')#Adding qualifier to all statements (P131)
#     else:
#         print('Qualifier (P100) already exists.')


#Removing qualifier one at a time-----------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Remove a qualifier from claims/statements
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")
# item.get() #Fetch all page data, and cache it.

# for claim in item.claims['P769']: #Finds all statements (P131)
#     if 'P100' in claim.qualifiers: #If has the qualifier we want to remove
#         for qual in claim.qualifiers['P100']: #iterate over all P100
#             claim.removeQualifier(qual, summary=u'Remove qualifier.') #remove P100
#     else:
#         print('No qualifier (P100)')

#Removing multiple qualifiers at a time----------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Remove a qualifiers form claims/statements
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")
# item.get() #Fetch all page data, and cache it.

# #DON'T program like this. It's just to show the function 'removeQualifiers()'.
# claim = item.claims['P115'][0] #Claim
# qual_1 = claim.qualifiers[u'P580'][0] #qualifier
# qual_2 = claim.qualifiers[u'P88'][0] #qualifier
# claim.removeQualifiers([qual_1, qual_2], summary=u'Removes 2 qualifiers.') #Remove both in ONE edit. Uses list.