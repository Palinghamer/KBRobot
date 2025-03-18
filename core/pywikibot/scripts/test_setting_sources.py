# # -*- coding: utf-8  -*-
# import pywikibot
# import time
# from datetime import date
# """
# Adding sources to newly-created claim/statement
# """
# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723")

# #CLAIM
# claim = pywikibot.Claim(repo, u'P82') #Adding instance of (P82)
# target = pywikibot.ItemPage(repo, u"Q187962") #Connecting P82 with Wikibase item (Q187962)
# claim.setTarget(target) #Set the target value in the local object.
# item.addClaim(claim, summary=u'Adding claim to Q238723') #Inserting value with summary to Q4115189

# #ADDS TWO REFERENCES
# #FIRST REF.
# today = date.today() #Date today
# ref = pywikibot.Claim(repo, u'P149') #stated in (P149)
# ref.setTarget(pywikibot.ItemPage(repo, 'Q238723')) #Connecting P248 with Google Knowledge Graph (Q648625), that is a Q-id. example stated in -> Google Knowledge Graph).

# #SECOND REF.
# retrieved = pywikibot.Claim(repo, u'P388') #retrieved (P388). Data type: Point in time
# dateCre = pywikibot.WbTime(year=int(today.strftime("%Y")), month=int(today.strftime("%m")), day=int(today.strftime("%d"))) #retrieved -> %DATE TODAY%. Example retrieved -> 29.11.2020
# retrieved.setTarget(dateCre) #Inserting value

# claim.addSources([ref, retrieved], summary=u'Adding sources to administrative territorial entity (P82).')

#How to add sources to existing statements-------------------------

#This code checks for a certain source and adds it if it is not present. 

# # -*- coding: utf-8  -*-
# import pywikibot
# from datetime import date
# """
# Add source to existing statement/claim.
# """

# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723") 
# item.get()

# if item.claims['P125']:
#     for claim in item.claims['P125']: # Loop through items
#         already = False
#         try:
#             srcs = claim.getSources() # Gets all of the source on the claim
#         except:
#             continue
#         for src in srcs: # Loop through sources
#             if "P74" in src: # If someone is using P74 already change variable "already" to TRUE
#                 already = True
#         if already: # If True skip this claim
#             print("Claim has already P74 as source! skipping!")
#             continue
#         #ADD A REF.
#         today = date.today() #Date today
#         retrieved = pywikibot.Claim(repo, u'P74', is_reference=True) # retrieved (P813 - wikidata) or date (P74 - test wd) . Data type: Point in time
#         dateCre = pywikibot.WbTime(year=int(today.strftime("%Y")), month=int(today.strftime("%m")), day=int(today.strftime("%d"))) # retrieved -> %DATE TODAY%. Example retrieved -> 29.11.2020
#         retrieved.setTarget(dateCre) #Inserting value
    
#         claim.addSource(retrieved, summary=u'Adding source.')
#         print('Source added!')
#         break # Make your own logic for finding the correct claim. In this example we just takes the first
# else:
#     print("missing P131 on item!")

#Removing sources---------------------------------------------

# # -*- coding: utf-8  -*-
# import pywikibot
# """
# Remove sources on existing statement/claim.
# """

# site = pywikibot.Site("test", "wikidata")
# repo = site.data_repository()
# item = pywikibot.ItemPage(repo, "Q238723") 
# item.get()

# if item.claims['P82']: # Check if it has the the property P82 on the item
#     for claim in item.claims['P82']: # Loop through claims
#         if not claim.sources: # If empty list/no source on the claim
#             print("Claim has no source(s)")
#             continue # Continue to next claim
#         sources = [] # list of all the source(s) on the claim
#         for source in claim.sources: # Loop through sources on claim
#             for value in source.values():  # Loop through source values on claim
#                 sources.extend(value) # add it to the list
#         claim.removeSources(sources, summary=u'Removed source(s).') # Remove all of the source(s) added in the list
#         print('Source(s) removed!')
#         break # Make your own logic for finding the correct source(s) in this example we just takes the first
# else:
#     print("Missing P82 on item!")
