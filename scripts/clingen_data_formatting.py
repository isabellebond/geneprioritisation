import pandas as pd
import os
import logging

PROJECT_PATH = '/Users/isabellebond/Documents/PhD_projects.nosync/geneprioritisation/'
DATA_PATH = os.path.join(PROJECT_PATH, 'data')

#Create logging file for data formatting and missing data
logging.basicConfig(
    filename=os.path.join(PROJECT_PATH, 'logging','clingen_data_formatting.log'),                # Log file name
    filemode='w',                      # Append mode ('w' for overwrite)
    level=logging.DEBUG,               # Set the minimum logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
###########################################################
# Format ClinGen data
###########################################################
clingen = pd.read_csv(os.path.join(DATA_PATH, 'rawdata', 'Clingen-Gene-Disease-Summary-2025-01-09.csv'), skiprows = 4)
clingen = clingen.rename(columns = {'GENE SYMBOL' : 'gene_name',
                                    'GENE ID (HGNC)': 'hgnc_id',
                                    'DISEASE LABEL': 'disease_label',
                                    'DISEASE ID (MONDO)': 'mondo_disease_id',
                                    'CLASSIFICATION': 'classification'})
clingen = clingen[['gene_name', 'hgnc_id', 'disease_label', 'mondo_disease_id', 'classification']]
clingen['mondo_disease_id'] = clingen['mondo_disease_id'].str.replace(':', '_')

#Load ensembl data 
ensembl = pd.read_csv(os.path.join(DATA_PATH, 'formatteddata', 'ensembl.genes.txt'), sep = '\t')

clingen_ensembl = clingen.merge(ensembl, on = 'gene_name', how = 'left')

#Check for missing data
missing_data = clingen_ensembl.loc[clingen_ensembl['gene_id'].isnull()].gene_name.unique()
logging.info(f'ClinGen data missing Ensembl gene IDs for: {missing_data}')

#Add disease ancestor information
disease_ancestors = pd.read_csv(os.path.join(DATA_PATH, 'ontologymapping', 'mondo.humandisease.descendants.txt'), sep = '\t')
disease_ancestors = disease_ancestors.rename(columns = {'Ontology ID': 'mondo_disease_id', 'Ancestor': 'mondo_ancestor_id'})

clingen_ensembl = clingen_ensembl.merge(disease_ancestors, on = 'mondo_disease_id', how = 'left')

#Check for missing data
missing_data = clingen_ensembl.loc[clingen_ensembl['mondo_ancestor_id'].isnull(), ['disease_label', 'mondo_disease_id']]
missing_data = missing_data.drop_duplicates()
missing_data.to_csv(os.path.join(DATA_PATH, 'missingdata', 'clingen.missing_ancestor_ids.txt'), sep = '\t', index = False)
logging.info(f'ClinGen data missing MONDO ancestor IDs for: {missing_data}')
logging.info(f'ClinGen disease ancestors are: {clingen_ensembl.mondo_ancestor_id.unique()}')