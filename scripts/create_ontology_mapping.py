import pandas as pd
from funcs.ontology_lookups import get_direct_descendants, get_all_descendants
import os

DATA_PATH = '/Users/isabellebond/Documents/PhD_projects.nosync/geneprioritisation/data'
#####################################################################################################
# Step 0: Load Clingen data and format with ensembl info
#####################################################################################################

#####################################################################################################
# Step 1: Match clingen disease terms to MONDO ancestor terms using the ontology_lookups.py functions
#####################################################################################################
#Directly access functions to quickly test them
ontology = 'http://purl.obolibrary.org/obo/mondo.owl'
namespace = 'http://purl.obolibrary.org/obo/'
entity = 'MONDO_0700096'

human_disease_descendants = get_direct_descendants(ontology, namespace, 'MONDO_0700096')
human_disease_descendants.to_csv(os.path.join(DATA_PATH, 'ontologymapping', 'mondo.humandisease.txt'), sep = '\t')

#Get all descendants
diseases = []
for disease in human_disease_descendants['Ontology ID']:
    descendants = get_all_descendants(ontology, namespace, disease)
    print(descendants)
    descendants['Ancestor'] = disease
    diseases.append(descendants)
    
diseases = pd.concat(diseases, ignore_index=True)
diseases.to_csv(os.path.join(DATA_PATH, 'ontologymapping', 'mondo.humandisease.descendants.txt'), sep = '\t')