import pywikibot
from pywikibot.data import api
import pprint
import json
import pandas as pd

#Reading csv into a DF----------------------------------------------------------

def read_csv_to_df(path):
    """
    Reads a CSV file into a Pandas DataFrame.
    
    Parameters:
    file_path (str): The path to the CSV file.
    
    Returns:
    pd.DataFrame: The resulting DataFrame.
    """
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
    
df = read_csv_to_df("test3.csv")

#Settings for test-Wikidata connection---------------------------------------------

site = pywikibot.Site("test", "wikidata")
repo = site.data_repository()


#API request------------------------------------------------------------------------

def get_items(site, item_title):
    """
    Requires a site and search term (item_title) and returns the results.
    """
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": item_title
              }
    request = api.Request(site=site, parameters=params)
    response = request.submit()
    # print(json.dumps(response, indent=4))
    return response

# get_items(site, item_title)

#Check if item exists-----------------------------------------------------------------


#Please do not run this script multiple times in a row because this will result in the creation of multiple items

#Requires safeguard so script can only be ran once every 5 minutes. Print message in console when blocking execution. 


def check_item_exists(site, item_title):
    """
    Checks if a Wikidata item exists by querying the search API.
    Returns the item ID if exactly one result is found, or None otherwise.
    """
    search_results = get_items(site, item_title)
    
    if len(search_results["search"]) == 1:
        return search_results["search"][0]["id"]
    else:
        return None

def check_item_exists(site, item_title):
    search_results = get_items(site, item_title)

    if "search" in search_results and len(search_results["search"]) > 0:
        # Return the first matching item's ID
        return search_results["search"][0]["id"]
    return None

#Create new item if item doesn't already exist------------------------------------------

def create_item(site, label_dict):
    new_item = pywikibot.ItemPage(site)
    new_item.editLabels(labels=label_dict, summary="Creating a new item with specified labels.")
    return new_item.getID()

# Main function to check if an item exists, if not, create a new one

def check_and_create_item(site, item_title):
    # Check if the item exists
    item_id = check_item_exists(site, item_title)
    
    if item_id:
        print(f"Item with title '{item_title}' already exists with ID: {item_id}")
    else:
        print(f"Item with title '{item_title}' does not exist. Creating a new item...")
        
        # Define labels for the new item (can be customized or pulled from a CSV or external source)
        some_labels = {"en": item_title, "de": item_title}  # You can add more languages here
        new_item_id = create_item(site, some_labels)
        
        print(f"New item created with ID: {new_item_id}")

# check_and_create_item(site, item_title)


#Setting claims & sources----------------------------------------------------------------

#Make this dynamic based on P-id's in column headers so adding column headers to .csv file doesn't break the script: loop over the column headers, extract the P-id and add this to the item (using regex). 

#Find out a way to enter string/item link etc depending on what is appropriate 

#CAREFUL: While this is dynamic, the values inside the fields should be of the correct type for the corresponding properties (i.e., string, item, quantity, etc.)


# item = pywikibot.ItemPage(repo, "Q238723") # need to replace this with something that can be looped over 

# def add_claims(site, repo, item_title):

# claim = pywikibot.Claim(repo, u'P82') #Adding 'instance of '(P31)
# target = pywikibot.ItemPage(repo, u"Q300") #Connecting P31 with sandbox (Q300)
# claim.setTarget(target) #Set the target value in the local object.


# stringclaim.setTarget(u"https://test.wikidata.org/wiki/Q238723") #Using a string
# item.addClaim(stringclaim, summary=u'Adding string claim')






#Check if claims & sources in existing item == claims & sources in .CSV------------------

#With this function simply check if the existing items already have a value that is the same as the value in the .csv file. If not: remove the statement, log its previous value, and add the correct claim. 






#Loop over df to add items---------------------------------------------------------------

def process_csv_and_create_items(df, site):
    """
    Processes each row of the DataFrame and calls check_and_create_item for each row.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing the CSV data.
    site: The Wikidata site object.
    """
    for index, row in df.iterrows():
        item_title = row['Title']  # Access the Title value for each row
        check_and_create_item(site, item_title)  
process_csv_and_create_items(df, site)





#Loop over items to add claims & sources---------------------------------------------------











#Obsolete snippets----------------------------------------------------------------

# for index, row in df.iterrows():
#     print(f"Index: {index}, Author: {row.get('P50 (author)', 'N/A')}, Contributors: {row.get('P767 (contributors)', 'N/A')}, "
#           f"Publication date: {row.get('P577 (publication date)', 'N/A')}, Publisher: {row.get('P123 (publisher)', 'N/A')}, "
#           f"Instance of: {row.get('P31 (instance of)', 'N/A')}, Instance of 2: {row.get('P31 (instance of 2)', 'N/A')}, "
#           f"Language: {row.get('P407 (language)', 'N/A')}, Distributed by: {row.get('P750 (distributed by)', 'N/A')}, "
#           f"Fabrication method: {row.get('P2079 (fabrication method)', 'N/A')}, Software engine: {row.get('P408 (software engine)', 'N/A')}, "
#           f"Programmed in: {row.get('P277 (programmed in)', 'N/A')}, Genre: {row.get('P136 (genre)', 'N/A')}, "
#           f"Subject: {row.get('P921 (main subject)', 'N/A')}, URL: {row.get('P2699 (URL)', 'N/A')}, "
#           f"Archive URL: {row.get('P1065 (archive URL)', 'N/A')}, Presented in: {row.get('P5072 (presented in)', 'N/A')}")


# def create_item(site, label_dict):
#     """
#     Creates new item with name and label item_title (title field in csv)
#     """    
#     new_item = pywikibot.ItemPage(site)
#     label_dict = {"en": item_title}
#     new_item.editLabels(labels=label_dict, summary="Creating a new item with specified labels.")
#     return new_item.getID()