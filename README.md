# KBRobot

> ⚠️ **Warning:** To avoid accidental vandalism, it is critical that the data provided to the bot is correct and adheres to [Wikidata policies and guidelines](https://www.wikidata.org/wiki/Wikidata:List_of_policies_and_guidelines), including the [notability criterion](https://www.wikidata.org/wiki/Wikidata:Notability).

### About

This project automates item creation and setting statements on [Wikidata](https://www.wikidata.org) for electronic literature works archived by the [Laboratory for Electronic Literature](https://www.kbr.be/en/projects/laboratory-for-electronic-literature/) at KBR. The bot takes a structured .CSV file, checks for existing items based on the title of the work, creates a new item if none exist, and sets the recorded claims and sources automatically.

### Data model

Metadata about the works are encoded according to the LabEL ontology recorded [here](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL). Please refer to the graph below for a graph of the current ontology.

![Ontology graph](ontology/LabEL_ontology_V5.png)
_Figure 1: Visualisation of the LabEL ontology._

<u>**Note:**</u> this schema serves to help understand the data model and does not fully reflect the logic of the actual Wikidata model. Properties and their targets are represented as classes and subclasses rather than items and properties.

### Upcoming changes

- [x] Support for dates
- [ ] Logging changes made
- [ ] Guidelines for structured data entry
- [ ] Documentation for scripts & pywikibot
