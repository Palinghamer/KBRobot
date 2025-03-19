#KBRobot

This bot automates item creation and population on [Wikidata](https://www.wikidata.org) for electronic literature works archived by the [Laboratory for Electronic Literature](https://www.kbr.be/en/projects/laboratory-for-electronic-literature/) at KBR.

Metadata about the works are encoded according to the LabEL ontology recorded [here](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL).

![Ontology graph]()

The bot takes a structured .CSV file, checks for existing items based on the title of the work, creates a new item if none exist, and adds the recorded claims and sources automatically. For this reason it is crucial that data fed to the bot are accurate and follow [Wikidata policies and guidelines](https://www.wikidata.org/wiki/Wikidata:List_of_policies_and_guidelines), especially the [Notability criteria](https://www.wikidata.org/wiki/Wikidata:Notability).

Soon, this project will be updated with: (1) guidelines for structured data entry that are in line with Wikidata policies and guidelines; and (2) documentation of the scripts used for this project and how to edit or add to them.
