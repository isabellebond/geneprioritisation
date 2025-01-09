rawdata:
- Clingen-Gene-Disease-Summary-2025-01-09.csv:
    - downloaded from: https://search.clinicalgenome.org/kb/gene-validity/download
    - download data: 09/01/25
    - summary: A file listing all gene-disease relationships in clingen
- ensembl
    - downloaded from: https://ftp.ensembl.org/pub/current_gtf/homo_sapiens/ and https://ftp.ensembl.org/pub/current_tsv/homo_sapiens/
    - download date: 09/01/25
    - summary: Files containing information about curreny ensembl genes, transcripts etc.

missingdata:
A repository to store any instances where data is missing or unavailable
- clingen.missing_ancestor_ids.txt
    - clingen diseases that do not have an ancestor in MONDO 'human disease' direct descendants. This appears to be because the term has either been made 'obsolete' or the term refers to a susceptability to a disease rather than the disease itself.
