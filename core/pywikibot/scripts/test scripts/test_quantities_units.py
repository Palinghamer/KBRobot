import pywikibot
from pywikibot.data import api
import pprint

# FIXME Hardcoded for test.wikidata
# Define properties and data
p_stated_in = "P149"
p_half_life = "P525"
p_ref_url = "P93"
precision = 10 ** -10
# data = [quantity, uncertainty, unit (Q1748 = hours)]
# source = [stated in item, ref url]
half_life_data = {"uranium-240": {"data": ["14.1", "0.1", "Q1748"],
                                  "source": ["Q1751", "http://www.nndc.bnl.gov/chart/reCenter.jsp?z=92&n=148"]}
                  }

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()

def get_items(site, item_title):
    """
    Requires a site and search term (item_title) and returns the results.
    """
    params = {"action": "wbsearchentities",
              "format": "json",
              "language": "en",
              "type": "item",
              "search": item_title}
    request = api.Request(site=site, **params)
    return request.submit()

def check_claim_and_uncert(item, property, data):
    """
    Requires a property, value, uncertainty and unit and returns boolean.
    Returns the claim that fits into the defined precision or None.
    """
    item_dict = item.get()
    value, uncert, unit = data
    value, uncert = float(value), float(uncert)
    try:
        claims = item_dict["claims"][property]
    except:
        return None

    try:
        claim_exists = False
        uncert_set = False
        for claim in claims:
            wb_quant = claim.getTarget()
            delta_amount = wb_quant.amount - value
            if abs(delta_amount) < precision:
                claim_exists = True
            delta_lower = wb_quant.amount - wb_quant.lowerBound
            delta_upper = wb_quant.upperBound - wb_quant.amount
            check_lower = abs(uncert - delta_lower) < precision
            check_upper = abs(delta_upper - uncert) < precision
            if check_upper and check_lower:
                uncert_set = True

            if claim_exists and uncert_set:
                return claim
    except:
        return None

def check_source_set(claim, property, data):
    source_claims = claim.getSources()
    if len(source_claims) == 0:
        return False

    for source in source_claims:
        try:
            stated_in_claim = source[p_stated_in]
        except:
            return False
        for claim in stated_in_claim:
            trgt = claim.target
            if trgt.id == data[0]:
                return True

def set_claim(item, property, data):
    value, uncert, unit = data
    value, uncert = float(value), float(uncert)
    claim = pywikibot.Claim(repo, property)
    unit_item = pywikibot.ItemPage(repo, unit)
    entity_helper_string = "http://test.wikidata.org/entity/Q1748".format()
    wb_quant = pywikibot.WbQuantity(value, entity_helper_string, uncert)
    claim.setTarget(wb_quant)
    item.addClaim(claim, bot=False, summary="Adding half-life claim from NNDC.")
    return claim

def create_source_claim(claim, source_data):
    trgt_item, ref_url = source_data
    trgt_itempage = pywikibot.ItemPage(repo, trgt_item)
    source_claim = pywikibot.Claim(repo, p_stated_in, isReference=True)
    source_claim.setTarget(trgt_itempage)
    claim.addSources([source_claim])
    return True

for key in half_life_data:
    search_results = get_items(site, key)
    if len(search_results["search"]) == 1:
        item = pywikibot.ItemPage(repo, search_results["search"][0]["id"])
        data = half_life_data[key]["data"]
        source_data = half_life_data[key]["source"]

        claim = check_claim_and_uncert(item, p_half_life, data)
        if claim:
            source = check_source_set(claim, key, source_data)
            if source:
                pass
            else:
                create_source_claim(claim, source_data)
        else:
            claim = set_claim(item, p_half_life, data)
            create_source_claim(claim, source_data)
    else:
        print("No result or too many found for {}.", key)