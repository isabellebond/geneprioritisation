import pandas as pd
from funcs.ensembl_lookups import gtf_to_txt, get_canonical_transcripts, get_protein_information, get_entrez_ids
import os

PROJECT_PATH = '/Users/isabellebond/Documents/PhD_projects.nosync/geneprioritisation/'
DATA_PATH = os.path.join(PROJECT_PATH, 'data')

# Load the Ensembl gene information
ensembl_data = os.path.join(DATA_PATH, 'rawdata', 'ensembl', 'Homo_sapiens.GRCh38.113.gtf.gz')
df = gtf_to_txt(ensembl_data)
df.to_csv(os.path.join(DATA_PATH, 'formatteddata', 'ensembl.genes.txt'), sep = '\t')

#Get information on the canonical transcripts
canonical_data = os.path.join(DATA_PATH, 'rawdata', 'ensembl', 'Homo_sapiens.GRCh38.113.canonical.tsv')
df = get_canonical_transcripts(canonical_data, df)
print(df)

#Get proteins linked to the canonical transcript, and the associated uniprot (SWISSPROT) IDs
protein_data = os.path.join(DATA_PATH, 'rawdata', 'ensembl', 'Homo_sapiens.GRCh38.113.uniprot.tsv')
df = get_protein_information(protein_data, df, canonical_only = True)

#Get entrez IDs of genes
entrez_data = os.path.join(DATA_PATH, 'rawdata', 'ensembl', 'Homo_sapiens.GRCh38.113.entrez.tsv')
df = get_entrez_ids(entrez_data, df)

df.drop_duplicates(keep = 'first', inplace=True)

df.to_csv(os.path.join(DATA_PATH, 'formatteddata', 'ensembl.genes.txt'), sep = '\t', index = False)