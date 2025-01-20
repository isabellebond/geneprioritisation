import pandas as pd
from funcs.ontology_lookups import load_ontology, get_direct_descendants, get_all_descendants, get_term_from_label
from funcs.general import sep_cells
import os
from owlready2 import *

DATA_PATH = '/Users/isabellebond/Documents/PhD_projects.nosync/geneprioritisation/data'
#####################################################################################################
# Step 0: Load Clingen data and format with ensembl info
#####################################################################################################

#####################################################################################################
# Step 1: Match clingen disease terms to MONDO ancestor terms using the ontology_lookups.py functions
#####################################################################################################

#Directly access functions to quickly test them
#ontology = 'http://purl.obolibrary.org/obo/mondo.owl'
namespace = 'http://purl.obolibrary.org/obo/'
entity = 'MONDO_0700096'
'''
human_disease_descendants = get_direct_descendants(ontology, namespace, 'MONDO_0700096')
human_disease_descendants.to_csv(os.path.join(DATA_PATH, 'ontologymapping', 'mondo.humandisease.txt'), sep = '\t', index = False)

#Get all descendants
diseases = []
for i,row  in human_disease_descendants.iterrows():
    descendants = get_all_descendants(ontology, namespace, row['Ontology ID'])
    print(descendants)
    descendants['Ancestor'] = row['Ontology ID']
    descendants['Ancestor Name'] = row['Name']
    diseases.append(descendants)
    
diseases = pd.concat(diseases, ignore_index=True)
diseases.to_csv(os.path.join(DATA_PATH, 'ontologymapping', 'mondo.humandisease.descendants.txt'), sep = '\t', index = False)
'''
#####################################################################################################
# Create files to map to other ontology terms
#####################################################################################################
#load mapped ontology
mapper = pd.read_csv(os.path.join(DATA_PATH, 'ontologymapping', 'between.ontologies.txt'), sep = '\t')

ontology_namespace = {'hp': 'http://purl.obolibrary.org/obo/',
                      'efo': 'http://www.ebi.ac.uk/efo/',
                      'mp': 'http://purl.obolibrary.org/obo/'}
ontology_iri = {
                #'hp': 'http://purl.obolibrary.org/obo/hp/releases/2024-12-12/hp-international.owl',
              #'efo': 'http://www.ebi.ac.uk/efo/releases/v3.73.0/efo.owl',
              'mp': 'http://purl.obolibrary.org/obo/mp/mp-international.owl'}#,
              #'zfa': 'http://purl.obolibrary.org/obo/zfa.owl'}

ontology_parentterm = {#'hp': 'phenotypicabnormality',
                       'efo': 'measurement',
                       'mp': 'mammilianphenotype',
                       'zfa': 'ZFA_0000001'}

for ontology, iri in ontology_iri.items():
    print(ontology, ontology_namespace[ontology])
    obo, ont = load_ontology(iri, ontology_namespace[ontology])
    columnname = f'{ontology}_label'
    df = sep_cells(mapper, columnname)
    print(df)
    label_to_ont = []
    descendant_df = []
    for label in df:
        print(label)
        id = get_term_from_label(obo, label, ontology)
        label_to_ont.append(pd.DataFrame({f'{ontology}_label': [label], f'{ontology}_id': [id]}))
        descendants = get_all_descendants(ontology_namespace[ontology], id, names = False)
        descendants['Ancestor'] = id
        descendants['Ancestor Name'] = label
        descendant_df.append(descendants)
    
    descendant_terms = pd.concat(descendant_df)
    label_to_ont = pd.concat(label_to_ont)
    
    descendant_terms.to_csv(os.path.join(DATA_PATH, 'ontologymapping', f'{ontology}.{ontology_parentterm[ontology]}.descendants.txt'), sep = '\t', index = False)
    label_to_ont.to_csv(os.path.join(DATA_PATH, 'ontologymapping', f'{ontology}.{ontology_parentterm[ontology]}.clingen.txt'), sep = '\t', index = False)
