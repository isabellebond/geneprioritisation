# geneprioritisation
A gene prediction model for clingen

## Defining cases/controls
Clingen is a manually created resource of genes associated with rare(ish) disease.
The gene-disease validity dataset can be downloaded [here.](https://search.clinicalgenome.org/kb/downloads#section_gene-disease-validity)
[ClinGen gene disease summary data]( https://search.clinicalgenome.org/kb/gene-validity) from 11/09/24 was used to identify all relationships.
[Ensembl gene information](https://asia.ensembl.org/info/data/ftp/index.html) was downloaded on 10/10/24. FTP was used over the API due to the high number of genes queried. A README for the data can be found [here](https://ftp.ensembl.org/pub/release-112/gtf/homo_sapiens/README).

This is the dataset to be used for training/testing:
- The outcome is a prediction of whether a gene is involved in a disease within an organ system, ie. is a cardiovascular disease gene

| ClinGen Classification | Bin | Number of Gene-Disease Relationships |
|------------------------|-----|--------------------------------------|
| Definitive; Strong; Moderate | Case | 2136 |
| Disputed; Refuted; No Known Disease Relationship | Control | 246 |
| Limited | Removed from analysis | 405 |
