# KBRobot

This project automates item creation and population on [Wikidata](https://www.wikidata.org) for electronic literature works archived by the [Laboratory for Electronic Literature](https://www.kbr.be/en/projects/laboratory-for-electronic-literature/) at KBR. Metadata about the works are encoded according to the LabEL ontology recorded [here](https://www.wikidata.org/wiki/Wikidata:WikiProject_Digital_Narratives/LabEL). Please see the graph below for an overview.

![Ontology graph](https://upload.wikimedia.org/wikipedia/commons/9/9d/Ontology_chart.jpg)

The bot takes a structured .CSV file, checks for existing items based on the title of the work, creates a new item if none exist, and adds the recorded claims and sources automatically. FFor this reason, it is critical that the data provided to the bot is correct and adheres to [Wikidata policies and guidelines](https://www.wikidata.org/wiki/Wikidata:List_of_policies_and_guidelines), particularly the [notability criterion](https://www.wikidata.org/wiki/Wikidata:Notability).

### Future

Soon, this project will be updated with: (1) guidelines for structured data entry that are in line with Wikidata policies and guidelines; and (2) documentation of the scripts used for this project and how to edit or add to them.
