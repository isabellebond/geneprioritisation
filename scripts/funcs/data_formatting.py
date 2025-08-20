import pandas as pd
from funcs.general import sep_cells
import ast

def mondo_to_ontology(between_ontology_map, ontology_descendants, ontology_name):
    '''
    Map MONDO terms to ontology terms
    '''
    if ontology_name == 'mondo':
        between_ontology_map[f'{ontology_name}_label'] = between_ontology_map['mondo_ancestor_id']

    between_ontology_map = between_ontology_map[['mondo_ancestor_id', f'{ontology_name}_label']]
    between_ontology_map = sep_cells(between_ontology_map, f'{ontology_name}_label')
    
    ontology_descendants = ontology_descendants.rename(columns = {'Ontology ID': f'{ontology_name}_id',
                                                                  'Ancestor': f'{ontology_name}_ancestor_id'})

    if ontology_name == 'mondo':
        ontology_map = ontology_descendants.rename(columns = {'Ancestor Name': f'ontology_label',
                                                              'mondo_id': 'ontology_id'})
        
        ontology_map['ontology_ancestor_id'] = ontology_map['mondo_ancestor_id']
    else:
        ontology_map = between_ontology_map.merge(ontology_descendants, left_on = f'{ontology_name}_label', right_on = 'Ancestor Name', how = 'left')
        ontology_map = ontology_map.drop(columns = ['Ancestor Name'])
        ontology_map.rename(columns = {f'{ontology_name}_label': 'ontology_label', 
                                   f'{ontology_name}_id': 'ontology_id',
                                   f'{ontology_name}_ancestor_id': 'ontology_ancestor_id'}, inplace = True)
        
    ontology_map = ontology_map.drop_duplicates(keep = 'first')
    
    
    ontology_map = ontology_map[['mondo_ancestor_id', 'ontology_label', 'ontology_id', 'ontology_ancestor_id']]
    
    return ontology_map

def ontology_to_disease_gene(gene_disease_data, ontology_map, feature_data, phenotype_id, gene_id, value = False, value_id = None):
    '''
    Format data by mapping to ontology and ancestor
    '''
    
    feature_data = feature_data.rename(columns = {gene_id: 'gene_id', 
                                                  phenotype_id: 'ontology_id'})
        
    #Catch if ':' in ontology_id
    feature_data['ontology_id'] = feature_data['ontology_id'].str.replace(':', '_')
    feature_data = feature_data.merge(ontology_map, on = f'ontology_id', how = 'left')

    data = gene_disease_data.merge(feature_data, on = ['gene_id', 'mondo_ancestor_id'], how = 'inner')
    
    if value == True:
        data = data[['gene_name', 'gene_id','mondo_disease_id','mondo_ancestor_id', 'ontology_id', 'ontology_ancestor_id', value_id]]
    else:
        data = data[['gene_name', 'gene_id','mondo_disease_id','mondo_ancestor_id', 'ontology_id', 'ontology_ancestor_id']]

    data = data.drop_duplicates(keep = 'first')
    
    return data

# Helper function to safely parse lists
def safe_eval(val):
    if pd.isna(val) or val == "":  # Handle NaN or empty strings
        return []
    try:
        return ast.literal_eval(val)  # Try parsing the value
    except (ValueError, SyntaxError):
        return []  # Return an empty list if parsing fails
    
def read_and_explode_chembl(chembl_path):
    chembl_df = pd.read_csv(chembl_path, converters={
    "linkedDiseases.rows": safe_eval,
    "linkedTargets.rows": safe_eval
    })

    # Explode the parsed list columns
    chembl_df= chembl_df.explode("linkedDiseases.rows").explode("linkedTargets.rows").reset_index(drop=True)
    chembl_df.dropna(subset = ['linkedDiseases.rows','linkedTargets.rows'], inplace=True)
    chembl_df = chembl_df.sort_values(by = ['maximumClinicalTrialPhase'], ascending=False)
    chembl_df = chembl_df.drop_duplicates(keep = 'first', subset = ['id','linkedDiseases.rows', 'linkedTargets.rows'])

    chembl_df = chembl_df.rename(columns = {'id': 'drug_id','linkedDiseases.rows': 'ontology_id', 'linkedTargets.rows': 'gene_id', 'maximumClinicalTrialPhase': 'max_trial_phase'})
    chembl_df = chembl_df[['drug_id', 'ontology_id', 'gene_id', 'max_trial_phase']]

    return chembl_df

def read_and_explode_opentargets(opentargets_path, column_name, ontology_map, gene_disease_data):
    opentargets_df = pd.read_csv(opentargets_path, converters={
        'organs': safe_eval})
    
    # Explode the 'organs' column
    opentargets_df = opentargets_df.explode("organs").reset_index(drop=True)
    opentargets_df.dropna(subset = ['organs'], inplace=True)
    opentargets_df = opentargets_df.sort_values(by = [column_name], ascending=False)
    
    opentargets_df.rename(columns = {'id': 'gene_id', 'organs': 'opentargets_label'}, inplace=True)
    
    ontology_map = sep_cells(ontology_map, 'opentargets_label')

    opentargets_df = opentargets_df.merge(ontology_map, on = ['opentargets_label'], how = 'left')
    

    opentargets_df = opentargets_df[['gene_id', 'opentargets_label', 'mondo_ancestor_id', column_name]]
    
    opentargets_df = gene_disease_data.merge(opentargets_df, on = ['gene_id', 'mondo_ancestor_id'], how = 'inner')
    
    opentargets_df = opentargets_df.sort_values(by = [column_name], ascending=False)
    opentargets_df = opentargets_df.drop_duplicates(keep = 'first', subset = ['gene_id','mondo_disease_id'])

    opentargets_df = opentargets_df[['gene_name', 'gene_id', 'mondo_disease_id', 'mondo_ancestor_id', 'opentargets_label', column_name]]

    return opentargets_df

def format_protein_data(protein_path, gene_disease_data):
    protein_df = pd.read_csv(protein_path, sep = '\s+')

    protein_df.loc[:,'protein1'] = protein_df['protein1'].str.split('.').str[1]
    protein_df.loc[:,'protein2'] = protein_df['protein2'].str.split('.').str[1]

    protein_df = protein_df.rename(columns = {'protein1': 'linked_protein_id', 'protein2': 'protein_id'})

    #get clingen definitive genes
    definitive_genes = gene_disease_data.loc[gene_disease_data['classification'].isin(['Definitive', 'Strong'])]
    definitive_genes = definitive_genes.drop_duplicates(subset = ['gene_id', 'mondo_ancestor_id'], keep = 'first')
    definitive_genes = definitive_genes.rename(columns = {'protein_id': 'linked_protein_id'})

    definitive_genes = definitive_genes[['linked_protein_id', 'mondo_ancestor_id']]

    definitive_genes = definitive_genes.merge(protein_df, on = 'linked_protein_id', how = 'inner')

    all_genes = gene_disease_data.merge(definitive_genes, on = ['protein_id', 'mondo_ancestor_id'], how = 'inner')
    all_genes = all_genes[['gene_name', 'gene_id', 'mondo_disease_id', 'mondo_ancestor_id', 'protein_id', 'linked_protein_id','experimental']]
    score = all_genes.sort_values(by = ['experimental'], ascending=False)
    score = score.drop_duplicates(keep = 'first', subset = ['gene_id', 'mondo_ancestor_id'])

    link_count = all_genes.loc[all_genes['experimental'] > 0]

    link_count = link_count[['gene_name', 'gene_id', 'mondo_disease_id', 'mondo_ancestor_id', 'linked_protein_id','protein_id', 'experimental']].drop_duplicates(keep = 'first')

    #count number is wrong
    print(link_count)

    return score, link_count
    




