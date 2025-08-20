import pandas as pd
import os
import logging

PQTLS = '/Users/isabellebond/Documents/nikhil_mr/pqtl_search_list_stiffnesMRAnalysis.xlsx'

PROJECT_PATH = '/Users/isabellebond/Documents/PhD_projects.nosync/geneprioritisation/'
DATA_PATH = os.path.join(PROJECT_PATH, 'data')

###########################################################
# Format ClinGen data
###########################################################
pqtl = pd.read_excel(PQTLS, sheet_name = 'pqtl_search_list_stiffnesMRAnal')
pqtl = pqtl.rename(columns = {'term' : 'gene_name'})

#Load ensembl data 
ensembl = pd.read_csv(os.path.join(DATA_PATH, 'formatteddata', 'ensembl.genes.txt'), sep = '\t')

pqtl_ensembl = pqtl.merge(ensembl, on = 'gene_name', how = 'left')

#Check for missing data
missing_data = pqtl_ensembl.loc[pqtl_ensembl['gene_id'].isnull()].gene_name.unique()
print(f'ClinGen data missing Ensembl gene IDs for: {missing_data}')

pqtl_ensembl.to_csv(os.path.join('pqtl_ensembl.txt'), sep = '\t', index = False)

