
# LabELbot documentation

# Overview
> ⚠️ **Warning:** To avoid accidental vandalism to Wikidata, it is critical that the data provided to the bot is correct and adheres to the [policies and guidelines](https://www.wikidata.org/wiki/Wikidata:List_of_policies_and_guidelines), including the [notability criterion](https://www.wikidata.org/wiki/Wikidata:Notability).

The LabELbot automates item creation and population on [Wikidata](https://www.wikidata.org/) for electronic literature works archived by the [Laboratory for Electronic Literature](https://www.kbr.be/en/projects/laboratory-for-electronic-literature/) (LabEL) at KBR. It allows archivists to efficiently and accurately upload large amounts of structured data, in accordance with Wikidata  [policies and guidelines](https://www.wikidata.org/wiki/Wikidata:List_of_policies_and_guidelines). 

The script runs locally and interacts with the Wikidata API to make changes to the live database. It reads from a CSV, checks for the existence of items based on title and QID, creates items where they do not exist, and adds statements about the works as outlined in the [LabEL data model](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL). Please refer to the graph below for an overview of the current ontology.  

![Ontology graph](ontology/LabEL_ontology_V5.png)
*Figure 1: Visualisation of the LabEL ontology.*

Pre-existent items and statements are skipped to prevent erroneous edits. After execution, a CSV file is created containing the change history, summarising all actions taken or skipped, allowing the user to review manually and adjust items the bot identified as too risky to edit autonomously. 

# Installation instructions

## Requirements

- Python 3.12 or higher
- Pandas 2.2.3
- A local clone of this repository

## Installation

Clone the repository locally for usage and development purposes. Scripts should be run from the `/core` directory using `pwb.py`. This differs from installing Pywikibot via `pip`, where scripts can be executed directly without referencing `pwb.py`.

Clone this directory locally using `git`:

```bash
git clone https://github.com/Palinghamer/KBRobot.git
```

Navigate to `/core` :

```bash
cd pywiki/core
```

## Configuration login

To get started, create your `user-config` file using `generate_user_files.py`, this file contains the [Wikidata domain you intend to edit, as well as your login credentials](https://www.wikidata.org/wiki/Wikidata:Pywikibot_-_Python_3_Tutorial/Setting_up_Shop#Configuration).

Alternatively, use [Bot passwords](https://www.mediawiki.org/wiki/Special:BotPasswords) to allow access via the API without using the account’s main login credentials. A guide on how to configure this can be found [here](https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords).

> ⚠️ **Warning:** The configuration determines which Wikimedia site the bot will edit. When testing, the language and domain should be set to “test” to avoid edits to the live website.
> 

Generate your `user-config` file: 

```bash
python pwb.py generate_user_files.py #enter wikidata, wikidata + login
```

This will create a file in the `/core` directory named `user-config.py`.  Once the file has been created, it can also be edited manually. 

Log in using `login`:

```bash
python pwb.py login #enter pw
```

If you are uncertain for which website or account your current session has been configured, repeat the same command. 

To log back out, use `-logout`:

```bash
python pwb.py login -logout
```

# Usage instructions

## How does it work?

Once called, the bot loops through each item in a CSV file (e.g., works or authors). For each item, it first checks if it was already assigned a QID. If not, it searches Wikidata using the item’s title. If a matching item is found, it is skipped to let the user review this item manually to avoid potential errors. If no match is found, a new Wikidata item is created, and its QID is written to the CSV. The bot then adds descriptions, statements, and sources to the item. Statements are set using the property codes from the column headers and their corresponding row values. If an identical statement already exists, it is skipped to prevent duplication. Users can review these skipped statements if needed. 

> ⚠️ **Warning:** The script is time-gated by default and can only be ran once every 5 minutes. This is to prevent unintended duplicate edits to Wikidata. While the bot checks for duplicate items and statements, these safeguards are limited by the refresh rate of Wikidata’s indexing. Running the script multiple times in quick succession may thus result in duplicate items or statements.
> 

To avoid overloading the API, the bot also periodically pauses between requests. In addition, upon creating a new item, it enters a sleep cycle checking every minute if the new item has been indexed. If the item appears within 10 minutes, the script continues adding statements. Otherwise it moves on to the next item. QIDs for all newly created items are saved to the CSV, skipped items can be edited manually or automatically processed by rerunning the script. These pauses are thus desired behaviour; simply wait for the script to complete, then check the change history for a summary of what was updated or skipped. 

## Data

The bot takes a structured CSV file containing titles, QIDs, properties, items and values to be added to Wikidata. Templates can be found in `/core/data`. New formats can be created, but the structure of these CSVs should match the structure outlined in the `config.json` files at `/pywikibot/scripts/configs`. 

For a detailed explanation of how to create and populate a new CSV file, please refer to the chapter [Structuring and populating CSV files](#structuring-and-populating-csv-files). To learn how to describe electronic works in statements, see the [Annotation guidelines](#annotation-guidelines). For information about `config` files, please refer to  [Creating `config` files for new CSV structures](#creating-config-files-for-new-csv-structures).

## Running the bot

The script comes preconfigured to create and populate work or author items and can be called on any CSV file. As for this setup, the repository is cloned locally, it is necessary to use `pwb.py` to run scripts.

Before running the bot, make sure you are logged into the correct account and to the ***correct Wikimedia website***. From the `/core` directory, run `login`: 

```bash
python pwb.py login #enter pw
```

To run the bot, call `prototype_main.py` on the CSV file containing the data that you want to upload. The example below uses a relevant path to the data folder that is used to store the data sets, but the script can be called on any CSV file that is correctly structured:

```bash
python [pwb.py](http://pwb.py/) prototype_main.py data/test_data.csv  
```

The script is preconfigured to create and populate items for authors *or* for works. To begin uploading authors, call with the `--mode author` argument:

```bash
python [pwb.py](http://pwb.py/) prototype_main.py data/test_data.csv --mode author 
```

For works use `—-mode work`: 

```bash
python [pwb.py](http://pwb.py/) prototype_main.py data/test_data.csv --mode work
```

Note: If no mode is specified, the script defaults to `work` mode. 

Before starting, the script will prompt the user to confirm pressing `Y` + `enter`:

```
You are about to run the script in AUTHOR mode. Editing Wikidata using the incorrect mode will result in unintended changes.
--- Continue? (Y/N):
```

Let the script run. A summary of actions undertaken or skipped will appear in the terminal upon completion, and a change history file will be added to the `/logs` folder for the user to validate the output.

## Change history and logs

Every time the script is ran, two files are created: a CSV file containing the history of changes made, and a .log file containing debugging information. Both are saved with timestamps in the folder `/logs` in the project root. 

If there is any uncertainty about the validity of an edit, the bot avoids actions like item creation or statement setting. It is therefore necessary for the user to validate the output, and to manually make edits to Wikidata where the bot did not. 

The user can refer to the change history to keep track of which items were created or which statements or sources were set, and which were skipped. The change history comes in a CSV file which can be filtered based on different variables, such as if an action was taken or skipped. This file is structured as follows:

| **Title** | **QID** | **Type** | **Action** | **Property** | **Value** |
| --- | --- | --- | --- | --- | --- |
| Aphorisms about birds | Q239198 | Claim | Skipped | P82 | Q215175 |
| Aphorisms about birds | Q239198 | Source | Created | P149 | Q239104 |

For debugging purposes, there is also a log with information about errors or skips. For future changes, this logging could be expanded.

## Structuring and populating CSV files

It is possible to add custom profiles to upload items that are not authors or works (such as events, for example), or that contain different properties. This can by done by defining your own CSV structure, mirroring its logic in a `config.json` file stored in the `/configs` folder, and adding this configuration as a `—-mode` in `profiles.json`. As noted above, Wikidata statements consist of a property and a corresponding value. Each column header in the CSV file represents a property ID, each row represents one item, and the values in the corresponding fields represent the value for that specific property. 

To define a statement with [instance of (P31)](https://www.wikidata.org/wiki/Property:P31), for example, enter the property ID (`P31`) as the column header and provide the appropriate value in each row (in this case, P31 expects an item Q-ID. Other value types could include dates, URLs, strings, etc.). 

Column headers can represent different statement properties such as simple properties, source properties, and descriptions.

### Statements

There are two required columns that every CSV must include as the first and second columns: `Title` and `QID`. 

- `Title` is a human-readable label for the item in English. This is used to find or create the item and should **always** contain a value.
- `QID` is used to identify existing items on Wikidata. If a valid Q-ID is provided, the script updates that item. If the field is empty or invalid, the script attempts to create a new item using the value in the `Title` column.

Each remaining column corresponds to a Wikidata property, which expects a specific data type (e.g., item, string, date). Column headers can include any property, as long as they are correctly defined in the `property_map`. See the chapter [Creating `config` files for new CSV structures](#creating-config-files-for-new-csv-structures) for further elaboration. Depending on the property, the expected value formats are: 

| Type | Format | Example | Notes |
| --- | --- | --- | --- |
| `item` | Q-ID (e.g., `Q123`) | `Q456; Q789` | Use semicolons to separate multiple QIDs. |
| `string` | Free text | `"My Value"` | Enter plain text. Avoid special characters that may break parsing. |
| `date` | ISO or natural format | `2020-01-01` or `Jan 1, 2020` | Will be auto-parsed. Invalid dates will be skipped. |

Multiple Q-IDs can be entered into a single field for item-type properties. When the script is run, each will be added as a separate statement. Use semicolons to separate them. 

### Sources

In addition to standard statements, you can and *should* specify **sources** for claims. These follow the same structure and must be defined in the `source_map`, specifying the source property, the type of the value, and which claim(s) it applies to. Learn how to do this in the chapter [Creating `config` files for new CSV structures](#creating-config-files-for-new-csv-structures) below. 

### Descriptions

**Descriptions for items are handled separately from claims and sources.** They do **not** need to be included in the `property_map` or `source_map`. Description fields always contain plain text strings. The target language is determined dynamically by the language code included in the column name. To be recognised correctly, description columns must follow this naming format: `description_xx`, where `xx` is a valid Wikidata language code (e.g., `en` for English, `fr` for French, `de` for German, etc.). 

### Example CSV

An example of a custom CSV could be:

| Title | QID | P1 | P2 | description_en | description_de |
| --- | --- | --- | --- | --- | --- |
| Novel title |  | Q123; Q456 | 2000-01-01 | Classic novel | Klassischer Roman |

```
Title,QID,P1,P2,description_en,description_de
The Great Novel,,Q123;Q456,2000-01-01,Classic novel, Klassischer Roman
```

Note: when string values contain commas, quotation marks are needed. 

This CSV format allows for flexible and structured data entry that mirrors Wikidata’s data model. To ensure correct statement setting, please refer to the chapter [Creating `config` files for new CSV structures](#creating-config-files-for-new-csv-structures) below to learn how to map properties and sources to their data types. Refer to the chapter [Annotation guidelines](#annotation-guidelines) for an overview of the different properties and annotation best practices. 

## Creating `config` files for new CSV structures

To use a new CSV structure, its logic must be reflected in a `config.json` file stored in the `/configs` directory, and it must be added as a `--mode` entry in `profiles.json`.

As noted above, each column header in the CSV file represents a **property ID**, and the values in the rows represent the **value** for that property. To define statements, enter the **property ID** (e.g., `P31`) as the column header and provide the appropriate value in each row (such as QIDs, dates, URLs, sources, etc.). 

> ⚠️ **Warning:** The first two columns of the CSV must *always* be “**Title**” and “**QID**”. These are fixed and should **not** be renamed or reconfigured, as they are critical for identifying, populating, or creating each item accurately.
> 

The CSV’s can be located anywhere on your machine, but there is dedicated folder reserved for data files at the relative path `/core/data` where the template CSV’s for work and author items are saved. 

Next, to ensure that statements are correctly set, it is necessary to specify the expected data types of the properties in the `config.json` , which can be found at the relative path `/pywikibot/scripts/configs`. This allows the configuration to translate CSV column data into structured statements with appropriate data types. The configuration files mirror the structure of the corresponding CSV files, specifying properties and their associated sources. For example, for data related to a work:

```json
{
  "property_map": {
    "P50": { "property": "P50", "type": "string" },
    "P767": { "property": "P767", "type": "string" },
    "P761": { "property": "P761", "type": "date" },
    "P145": { "property": "P145", "type": "item" },
    "P31": { "property": "P31", "type": "string" },
    "P31_2": { "property": "P31", "type": "string" },
    "P82": { "property": "P82", "type": "item" }
  },
  "source_map": {
    "P149": { "property": "P149", "type": "item", "targets": ["P82"] }
  }
}
```

As visible in the above example, this is a JSON file consisting of two main sections: `property_map` and `source_map`. The `property_map` defines the properties expected in the CSV file. Each key corresponds to a column header in the CSV, and the value is an object specifying: the target **property ID**, the data type of the **value** (e.g. , “string”, “date”, or “item”). The `source_map` is used to define references or sources for the data. Each entry represents a **source property** and includes:  the **source property ID**, the type of source, **and an array listing which properties in the `property_map` this source applies to.**

Note that it is not strictly necessary to add entries to `property_map` or `source_map` if you are not including statements or sources in your setup. However, both keys should still be present in the configuration file and can be left empty if unused. 

Finally, to add the configuration as a `--mode`, add a new key-value pair to the `profiles.json` file in `/pywikibot/scripts`, where the key is the mode name and the value is the relative path to the `config.json` file: 

```json
{
  "author": "configs/config_authors.json",
  "work": "configs/config_works.json",
}
```

You can now run the bot with this logic by specifying your newly created `--mode` in the same way you would for works or authors. 

# Structure of the code

The bot is built on a clone of the [Pywikibot](https://github.com/wikimedia/pywikibot) library. You can find the Pywikibot documentation [here](https://doc.wikimedia.org/pywikibot/stable/), and a comprehensive tutorial for using it with Wikidata is available [here](https://www.wikidata.org/wiki/Wikidata:Pywikibot_-_Python_3_Tutorial). 

While the complete tree of the project is much larger, below is an overview of the most important files and folders.

- **`logs/`** – Contains change history and log files.
- **`ontology/`** – Holds an approximate model of the ontology in Turtle format, along with visualisations.
- **`core/`** – Includes the complete library and custom scripts.
- **`data/`** – Used for storing CSV files.
- **`pywikibot/scripts/`** – Contains custom scripts organised into modules, which are imported by the main script, `prototype_main.py`. This is also where the configuration and profile files are located.

```bash

pywiki
├── logs/
├── ontology/               
├── core/                   
│   ├── data/
│   ├── user_config.py
│   ├── pywikibot/          
│   │   └── scripts/
│   │       ├── configs/
│   │       │   ├── config_works.json
│   │       │   ├── config_authors.json
│   │       │   └── config_custom.json
│   │       ├── generate_user_files.py
│   │       ├── prototype_main.py
│   │       ├── profiles.json
│   │       └── uploader.py
```

When making contributions to the code, please store your code in `pywikibot/scripts`. 

# Annotation guidelines

While the script can autonomously create items and upload data, it relies on accurate and structured input. Bots have the ability to make edits very quickly and can disrupt Wikidata if they are incorrectly designed or operated. 

[Incorrect operation](https://www.wikidata.org/wiki/Wikidata:Bots) can result in the creation of irrelevant or inaccurate items. Depending on the scale of the damage, an administrator may block the bot. It is therefore crucial that the data fed to the bot is accurate and correctly structured, and that the items created meet Wikidata’s [notability criterion](https://www.wikidata.org/wiki/Wikidata:Notability).

Below is an overview of the relevant notability criteria, bot requirements, the recommended data structure, and important considerations to keep in mind when annotating works. This is a summary, please refer to the [official guidelines](https://www.wikidata.org/wiki/Wikidata:Notability) for the full [documentation on notability](https://www.wikidata.org/wiki/Wikidata:Notability), the [bot policy,](https://www.wikidata.org/wiki/Wikidata:Bots) and the [LabEL data model](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL) for a complete overview. 

## Bot requirements

Bots have the ability to make edits very quickly, and can disrupt Wikidata if they are incorrectly designed or operated. For these reasons a [bot policy](https://www.wikidata.org/wiki/Wikidata:Bots) has been developed. 

As the contributions of a bot account remain the responsibility of its operator, the operator should be identified on its user page. In case of any damage **the bot operator is responsible** for cleaning up any damage caused by the bot. It is suggested the operator add the [bot policy](https://www.wikidata.org/wiki/Wikidata:Bots) page to their watchlist, as relevant notifications and discussions may take place on the [talk page](https://www.wikidata.org/wiki/Wikidata_talk:Bots). 

In the case of changes to the bot after its approval, the bot must stay within reasonable bounds of their approved tasks. If in doubt, file another request for approval. 

Specifically for statement adding bots such as this one, the following relevant requirements are in effect:

- Add sources to any statement that is added.
- Bots should add an [instance of (P31)](https://www.wikidata.org/wiki/Property:P31) and/or [subclass of (P279)](https://www.wikidata.org/wiki/Property:P279) if possible.
- Bots should check that they are not adding duplicate statements.
- Bots with a new source for an existing statement should add it as a new source, rather than create a new statement.

Every statement should have a source, which in the case of electronic works is LabEL, or perhaps the link to an event if this is cited. The instance of (P31) property is a structural property to all edits. The bot automatically checks for duplicate statements, however it ***does*** ***not*** control for typo’s or alternate spellings. It is therefore the responsibility of the bot operator to make sure the entered data is correct. 

## Notability criteria

All Wikidata items need to fulfil at leat one of the three following criteria:

1. It must contain **at least one valid [sitelink](https://www.wikidata.org/wiki/Special:MyLanguage/Help:Sitelinks)** to a page on Wikipedia, Wikivoyage, Wikisource, Wikiquote, Wikinews, Wikibooks, Wikidata, Wikispecies, Wikiversity, or Wikimedia Commons. 
2. It refers to an instance of a **clearly identifiable conceptual or material entity** that can be described using **serious and publicly available references**. 
3. It fulfils a **structural need**, for example: it is needed to make statements made in other items more useful. 

For works archived by LabEL, criteria 2 and 3 are generally the most relevant. Electronic works qualify as identifiable conceptual or material entities, and the LabEL database serves as a serious and publicly accessible reference, therefore meeting criteria 2. Items for authors, for example, also meet criteria 3 by fulfilling a structural role enabling more meaningful statements about works, by allowing properties to link to items rather than plain text strings.  

## The LabEL data model: node types and items

The data that is fed to the bot should be **correctly structured** and **accurate.** This means that properties should be matched with the correct data type, and that the items used accurately describe the work. 

### Node types

As outlined in the chapters [Structuring and populating CSV files](#structuring-and-populating-csv-files) and [Creating `config` files for new CSV structures](#creating-config-files-for-new-csv-structures), Wikidata statements consist of a subject, a property and a corresponding target value. In the CSV file, each column header represents a **property ID**, the rows represent items, and the values in the rows represent a **value** for that property. It is therefore important that the rows contain the valid data type for the corresponding property. A data type can be an item, another property, commons media, a quantity, coordinates, [a point in time](https://www.wikidata.org/wiki/Help:Data_type), a URL, a string, and so on. 

It is thus crucial that the CSV structure and `config` files mirror the [data model](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL) exactly, and that the row values match the expected item type and value for a particular type of item (e.g. work or author). Please refer to the table below for an overview of the different properties and node types used in the LabEL data model. 

**Node type: Creative works**

| **Property** | **Property ID** | **Data Type** | **Note** |
| --- | --- | --- | --- |
| [Author](https://www.wikidata.org/wiki/Property:P50) | P50 | Item |  |
| [Contributor to the creative work or subject](https://www.wikidata.org/wiki/Property:P767) | P767 | Item |  |
| [Publication date](https://www.wikidata.org/wiki/Property:P577) | P577 | Point in time |  |
| [Publisher](https://www.wikidata.org/wiki/Property:P123) | P123 | Item |  |
| [Instance of](https://www.wikidata.org/wiki/Property:P31) | P31 | Item | electronic literature (Q173167) – for all creative works |
| [Instance of](https://www.wikidata.org/wiki/Property:P407) | P31 | Item | Second value for 'instance of'. Instead of 'Form of creative work' because of the constraints |
| [Language of work or name](https://www.wikidata.org/wiki/Property:P407) | P407 | Item |  |
| [Distributed by](https://www.wikidata.org/wiki/Property:P750) | P750 | Item | 'Distribution platform' on the database |
| [Media modality](https://www.wikidata.org/wiki/Property:P12548) | P12548 | Item |  |
| [Fabrication method](https://www.wikidata.org/wiki/Property:P2079) | P2079 | Item |  |
| [Software engine](https://www.wikidata.org/wiki/Property:P408) | P408 | Item | Or "Depends on software" (P1547)? |
| [Programmed in](https://www.wikidata.org/wiki/Property:P277) | P277 | Item |  |
| [Genre](https://www.wikidata.org/wiki/Property:P136) | P136 | Item |  |
| [Main subject](https://www.wikidata.org/wiki/Property:P921) | P921 | Item |  |
| [URL](https://www.wikidata.org/wiki/Property:P2699) | P2699 | URL |  |
| [Archive URL](https://www.wikidata.org/wiki/Property:P1065) | P1065 | URL |  |
| [Copyright license](https://www.wikidata.org/wiki/Property:P275) | P275 | Item |  |
| [Presented in](https://www.wikidata.org/wiki/Property:P5072) | P5072 | Item | Event |
| Description |  | String |  |

**Node type: Authors**

| **Property** | **Property ID** | **Data Type** | **Note** |
| --- | --- | --- | --- |
| Instance of | P31 | Item | Human (Q5), Collective (Q13473501), or Organization (Q43229) |
| Influenced by | P737 | Item | A human, property or organization |
| Official website | P856 | URL |  |
| Description | — | String |  |

**If Human:**

| **Property** | **Property ID** | **Data Type** | **Note** |
| --- | --- | --- | --- |
| Date of birth | P569 | Point in time |  |
| Date of death | P570 | Point in time |  |
| Member of | P463 | Item | A collective or organization |

**If organisation or collective:**

| **Property** | **Property ID** | **Data Type** | **Note** |
| --- | --- | --- | --- |
| Start time | P580 | Point in time |  |
| End time | P582 | Point in time |  |

### Items for creative works

Beyond being of the correct data type, the values used in statements should accurately describe the work. For each property, there is a list of approved items, which can be expanded. For [Instance of (P31)](https://www.wikidata.org/wiki/Property:P31), these are items such as [blog (Q30849)](https://www.wikidata.org/wiki/Q30849), [electronic literature (Q173167)](https://www.wikidata.org/wiki/Q173167), [video game (Q7889)](https://www.wikidata.org/wiki/Q7889), [Internet bot (Q191865)](https://www.wikidata.org/wiki/Q191865), and so on.

Items can have multiple statements of the same property. For example, every work should be recorded as an [Instance of (P31)](https://www.wikidata.org/wiki/Property:P31) [electronic literature (Q173167)](https://www.wikidata.org/wiki/Q173167), as well as a different relevant item that describes the type or form of electronic literature. Similarly, works can have multiple authors, genres or modalities. If no adequate item exists, a statement can be left out, or a new item can be proposed to the project lead. 

As discussed in the chapter [Structuring and populating CSV files](#structuring-and-populating-csv-files), there are also structural values that should be part of the CSV, such as the title of the work and its Q-ID. 

Below is an overview of properties, with some of their associated values and possible ambiguities that should be taken into account during data entry. For a complete overview, please refer to the lists of approved items on the [LabEL data model page](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL#Items%20for%20%22Instance%20of%22).

[**Instance of (P31)**](https://www.wikidata.org/wiki/Property:P31)

Describes the type to which the subject corresponds/belongs to. Works recorded by LabEL are always an instance of [electronic literature (Q173167)](https://www.wikidata.org/wiki/Q173167). A second instance of statement is used to indicate the type of electronic literature. A work can also have more than two [Instance of (P31)](https://www.wikidata.org/wiki/Property:P31) statements. For example, a work could be software that is made available to visitors of a museum in an installation, in which case this item could simultaneously be an instance of [electronic literature (Q173167)](www.wikidata.org/wiki/Q173167), [software (Q7397)](https://www.wikidata.org/wiki/Q7397), and [installation artwork (Q20437094)](https://www.wikidata.org/wiki/Q20437094). The item should be described in its entirety, so in this case more is better. Nevertheless, it is important to choose the most specific item that accurately describes the subject. 

[**Language of work or name (P407)**](https://www.wikidata.org/wiki/Property:P407)

Describes the language associated with the creative work. A work can have multiple languages. Examples include: [Dutch (Q7411)](https://www.wikidata.org/wiki/Q7411), [English (Q1860)](https://www.wikidata.org/wiki/Q1860), [French (Q150)](https://www.wikidata.org/wiki/Q150). 

[**Distributed by (P750)**](https://www.wikidata.org/wiki/Property:P750)

Describes the distributor of a work such as a distributor for a record label or a news agency. This should not be confused with the [Publisher (P123)](https://www.wikidata.org/wiki/Property:P123) property. A work can have multiple [distributed by (P750)](www.wikidata.org/wiki/Property:P750) statements; all distribution platforms must be listed in separate statements, regardless of how many there are. Examples include: [App Store (Q368215)](https://www.wikidata.org/wiki/Q368215), [Steam (Q337535)](https://www.wikidata.org/wiki/Q337535), [GitLab (Q16639197)](https://www.wikidata.org/wiki/Q16639197), [Instagram (Q209330)](https://www.wikidata.org/wiki/Q209330). 

[**Media modality (P12548)**](https://www.wikidata.org/wiki/Property:P12548)

Describes which media modalities are present in a creative work, particularly in digital, multimodal works such as electronic literature. Not to be confused with [Fabrication method (P2079)](https://www.wikidata.org/wiki/Property:P2079). An item can contain multiple [media modality (P12548)](https://www.wikidata.org/wiki/Property:P12548) statements. Examples include: [audio recording (Q3302947)](https://www.wikidata.org/wiki/Q3302947), [image (Q478798)](https://www.wikidata.org/wiki/Q478798), [text (Q234460)](https://www.wikidata.org/wiki/Q234460). 

[**Fabrication method (P2079)**](https://www.wikidata.org/wiki/Property:P2079)

Describes the method, process or technique used to grow, build, assemble or manufacture the work. ****An item can contain multiple [fabrication method (P2079)](https://www.wikidata.org/wiki/Property:P2079) statements. This should again be as complete and accurate as possible. Depending on the work, it can be tricky to decide which item is most appropriate. The question should be asked what exactly the work *is*, and how it is assembled. For example, is a program that outputs poems fabricated using a [statistical method (Q12718609)](https://www.wikidata.org/wiki/Q12718609), [machine learning (Q2539),](https://www.wikidata.org/wiki/Q2539) [computer programming (Q80006)](https://www.wikidata.org/wiki/Q80006), or all perhaps any combination of the three? 

[**Software engine (P408)**](https://www.wikidata.org/wiki/Property:P408)

Describes the software engine employed by the subject item. An item can contain multiple [software engine (P408)](www.wikidata.org/wiki/Property:P408) statements. This information can often be found in the open code repositories maintained by the creators.  Examples include: [Unity (Q63966)](https://www.wikidata.org/wiki/Q63966),  [Adobe Flash (Q165658)](https://www.wikidata.org/wiki/Q165658). 

[**Programmed in (P277)**](https://www.wikidata.org/wiki/Property:P277)

Describes the programming language()s in which the software is developed. An item can contain multiple [programmed in (P277)](www.wikidata.org/wiki/Property:P277) statements. This information can again often be found in the open code repositories maintained by creators. Examples include: [Python (Q28865)](https://www.wikidata.org/wiki/Q28865), [Javascript (Q2005)](https://www.wikidata.org/wiki/Q2005), [HTML (Q8811)](https://www.wikidata.org/wiki/Q8811). 

[**Genre (P136)**](https://www.wikidata.org/wiki/Property:P136)

Describes a work’s genre. This is not the same as the creative work’s topic. ****An item can again have multiple [genre (P136)](https://www.wikidata.org/wiki/Property:P136) statements, however usually only one. The line can sometimes be blurry between [Instance of (P31)](https://www.wikidata.org/wiki/Property:P31) or [genre (P136)](https://www.wikidata.org/wiki/Property:P136) where genre is used to more generally situate the work. Examples include [Code poetry (Q17093921)](https://www.wikidata.org/wiki/Q17093921), [Generative art (Q1502032)](https://www.wikidata.org/wiki/Q1502032), [Interactive fiction (Q11431182)](https://www.wikidata.org/wiki/Q1143118), [Visual poetry (Q2578278)](https://www.wikidata.org/wiki/Q2578278). 

### Items for authors

Just as for works, there is a list of approved properties and items to be used when encoding authors or contributors. A work can have multiple contributors of different types such as [Human (Q5)](https://www.wikidata.org/wiki/Q5), [Collective (Q13473501)](https://www.wikidata.org/wiki/Q13473501), or [Organization (Q43229)](https://www.wikidata.org/wiki/Q43229). The properties for authors however, require less clarification. An overview of these properties and expected data types or items can be found on the [LabEL data model page](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL) or in the chapter [Node types](#structuring-and-populating-csv-files) above. 

# Licensing and Credits

