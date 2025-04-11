#!/usr/bin/python3

import pywikibot
from pywikibot import pagegenerators as pg

sparql_query = """
#Items that have a pKa value set
SELECT ?item ?value
WHERE
{
    ?item wdt:P1117 ?value . 
}
"""

file_path = "pka-query.rq"

with open(file_path, "w") as file:
    file.write(sparql_query)

with open('pka-query.rq', 'r') as query_file:
    QUERY = query_file.read()

wikidata_site = pywikibot.Site("wikidata", "wikidata")
generator = pg.WikidataSPARQLPageGenerator(QUERY, site=wikidata_site)

for item in generator:
    print(item)