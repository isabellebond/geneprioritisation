# geneprioritisation
A gene prediction model for clingen

## Defining cases/controls
Clingen is a manually created resource of genes associated with rare(ish) disease.

A dataset was created with:
- clingen gene-disease assertions
- ensembl info about the gene
- mondo ancestor information about the disease (for more info go to [ontology lookup service](https://www.ebi.ac.uk/ols4/ontologies/mondo))

To recreate you need to download:
- The clingen gene-disease validity [dataset](https://search.clinicalgenome.org/kb/downloads#section_gene-disease-validity)
- Ensembl [gtf file](https://ftp.ensembl.org/pub/current_gtf/homo_sapiens/)
- Ensembl [entrez and uniprot information files](https://ftp.ensembl.org/pub/current_tsv/homo_sapiens/)

Note: FTP was used over the API due to the high number of genes queried, for a small number of genes, chris has a [nice package](https://cfinan.gitlab.io/ensembl-rest-client/index.html) to query the api.

After download run clingen_data_formatting.py (update the file paths in main). This will create a dataset with relevant information for future analysis. 

Note: if a disease has multiple mondo ancestors that are direct descendants of the 'human disease' term, these will be recorded on separate lines.

This is the dataset to be used for creating cases and controls:
- The outcome is a prediction of whether a gene is involved in a disease within an organ system, ie. is a cardiovascular disease gene.
- Case control categories were based on ClinGen Classification, these numbers were correct as of Jan 2025 and may be slightly off now.

| ClinGen Classification | Bin | Number of Gene-Disease Relationships |
|------------------------|-----|--------------------------------------|
| Definitive; Strong; Moderate | Case | 2136  |
| Disputed; Refuted; No Known Disease Relationship | Control | 246 |
| Limited | Removed from analysis | 405 |

## Manual curation of mapping file between ontologies
Each unique moondo ancestor was saved to the file 'data/ontology_mapping.starter.txt.' To allow for collation of data between different datasets, each of these ancestors was mapped to either a relevant ontology term or a data subsection if relevant:

| Ontology/ Labelling Scheme | Ontology Term | Dataset |
|------------------------|-----|--------------------------------------|
| Mondo | human disease | ClinGen |
| Mammilian phenotype ontology | mammalian phenotype | Mouse Genome Informatics  |
| UK Biobank Chapter Encoding |  | AZ PheWAS |
| Experimental Factor Ontology | disease | Opentargets Locus2Gene |
| Human Phenotype Ontology | Phenotypic abnormality | Chembl |
| Opentargets organ systems | | RNA/Protein Expression |

This data is saved in 'data/ontology_mapping.manualedits.txt

## Phenotype data used to input into feature matrix
- ** Not included ** Astra Zeneca rare variant burden testing results. I didn't incorporate this into files as they have now released a [WGS 500K dataset](https://azphewas.com/about) (I was using 470K) - file headings may be different. You can email them to get the full dataset (CGR-Informatics-Support@astrazeneca.com.)
- Expression data from opentargets.
- Protein linking data from [String](https://string-db.org/cgi/download?sessionId=bscuhgQuCQxz) - detailed links file. Looking for known experimental links between known cligen genes involved in disease and the genes of interest. A link is said to have moderate evidence if the experimental score is above 400. Data for all links with non-zero data is recorded. If there is more than one protein with a link, values are separated by '; '.

