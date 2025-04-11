import pywikibot
from pywikibot.data import api
import pprint
import json
import pandas as pd
import re

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()
property_id = "P94"
datatype = repo.get_property_type(property_id)
print(datatype)
