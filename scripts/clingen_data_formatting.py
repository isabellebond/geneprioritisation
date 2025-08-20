import pandas as pd
import os
import re

from funcs.ontologies import load_ontology, get_descendants

def load_clingen_data(path):
    #Load data downloaded directly from ClinGen
    clingen = pd.read_csv((path), skiprows = 4)
    clingen = clingen.rename(columns = {'GENE SYMBOL' : 'gene_name',
                                        'GENE ID (HGNC)': 'hgnc_id',
                                        'DISEASE LABEL': 'disease_label',
                                        'DISEASE ID (MONDO)': 'mondo_disease_id',
                                        'CLASSIFICATION': 'classification'})
    clingen = clingen[['gene_name', 'hgnc_id', 'disease_label', 'mondo_disease_id', 'classification']]
    clingen['mondo_disease_id'] = clingen['mondo_disease_id'].str.replace(':', '_')

    return clingen

def parse_attributes(attribute):
    # Regular expression to extract key-value pairs
    pattern = re.compile(r'(\S+) "([^"]+)"')
    matches = pattern.findall(attribute)
    return {key: value for key, value in matches}

def gtf_to_txt(ensembl_data, chunksize = 10000):
    """
    Convert Ensembl GTF data to a DataFrame with relevant columns.
    Keep only protein-coding genes with a transcript support level of 1.
    """
    
    data_header = ['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attribute']

    processed_chunks = []

    # Read the Ensembl gene information in chunks
    for chunk in pd.read_csv(ensembl_data, names=data_header, sep='\t', skiprows=5, chunksize=chunksize):
        # Apply the function to the attribute column
        attributes_df = chunk['attribute'].apply(parse_attributes).apply(pd.Series)
        print(attributes_df, attributes_df)

        # Merge the new columns with the original DataFrame
        chunk = pd.concat([chunk, attributes_df], axis=1)
        print(chunk, chunk.columns)

        # Filter rows where feature is 'gene'
        chunk = chunk[chunk['feature'] == 'gene']
        print(chunk, chunk.columns)

        # Select the specified columns
        chunk = chunk[['seqname', 'start', 'end', 'strand', 'gene_id', 'gene_name', 'gene_biotype']]
        chunk = chunk.loc[((chunk['gene_biotype'] == 'protein_coding'))]
        chunk = chunk.drop(columns = ['gene_biotype'])
        chunk = chunk.rename(columns = {'seqname':'chromosome'})

        # Append the processed chunk to the list
        processed_chunks.append(chunk)

        # Concatenate all processed chunks
        ensembl_info = pd.concat(processed_chunks, ignore_index=True)

    return ensembl_info

def get_protein_information(protein_data, df):
    
    protein_info = pd.read_csv(protein_data, sep = '\t')
    #Keep only SWISSPROT IDs
    protein_info = protein_info.loc[protein_info['db_name'] == 'Uniprot/SWISSPROT']

    protein_info = protein_info.rename(columns = {'gene_stable_id':'gene_id',
                                                  'transcript_stable_id':'transcript_id',
                                                  'protein_stable_id':'protein_id',
                                                  'xref':'uniprot_id'})
    
    protein_info = protein_info[['gene_id', 'transcript_id', 'protein_id', 'uniprot_id']]
    
    df = pd.merge(df, protein_info, on = ['gene_id'], how = 'left')

    return df

def get_entrez_ids(entrez_data, df):
    
    entrez_info = pd.read_csv(entrez_data, sep = '\t')

    entrez_info = entrez_info.rename(columns = {'gene_stable_id':'gene_id',
                                                  'xref':'entrez_id'})
    
    entrez_info = entrez_info[['gene_id', 'entrez_id']].drop_duplicates(keep = 'first')
    
    df = pd.merge(df, entrez_info, on = 'gene_id', how = 'left')

    return df

def collate_ensembl_data(folder, prefix):
    '''
    Load ensembl data downloaded from ftp: https://ftp.ensembl.org/pub/
    - gtf: current_gtf/homo_sapiens/Homo_sapiens.GRCh38.114.gtf.gz
    - tsv: gunzip current_tsv/*<entrez and uniprot>*

    Need to save ensembl data in a single folder with specified prefix'''

    # Load the Ensembl gene information
    ensembl_data = os.path.join(folder, f'{prefix}.gtf.gz')
    df = gtf_to_txt(ensembl_data)
    print(df)

    #Get proteins linked to the canonical transcript, and the associated uniprot (SWISSPROT) IDs
    uniprot_data = os.path.join(folder, f'{prefix}.uniprot.tsv')
    df = get_protein_information(uniprot_data, df)
    print(df)

    #Get entrez IDs of genes
    entrez_data = os.path.join(folder, f'{prefix}.entrez.tsv')
    df = get_entrez_ids(entrez_data, df)
    print(df)

    df.drop_duplicates(keep = 'first', inplace=True)

    return df

def get_mondo_descendants():
    onto, mondo = load_ontology('http://purl.obolibrary.org/obo/mondo.owl','http://purl.obolibrary.org/obo/')

    #get direct descendants of human disease
    disease = get_descendants(mondo, 'MONDO_0700096', names = True, direct_only = True)

    #remove disease types unrelated to organ systems
    drop_terms = ['MONDO_0020683', #acute disease
                  'MONDO_0019040', #chromosomal disorder
                  'MONDO_0700220', #disease related to transplantation
                  'MONDO_0005066', #metabolic disease
                  'MONDO_0044970', #mitochondrial disease
                  'MONDO_0003847', #hereditary disease
                  'MONDO_0043543', #iatrogenic disease
                  'MONDO_0700007', #idiopathic disease
                  'MONDO_0005550', #infectious disease
                  'MONDO_0021166', #inflammatory disease
                  'MONDO_0005137', #nutrional disorder
                  'MONDO_0700003', #obstetric disorder
                  'MONDO_0100366', #occupational disorder
                  'MONDO_0100086', #perinatal disease
                  'MONDO_0029000', #poisoning
                  'MONDO_0021669', #post-infectious disorder
                  'MONDO_0019303', #preamature aging syndrome
                  'MONDO_0043459', #radiation-induced disorder
                  'MONDO_0002254', #syndromic disease
                  ]
    disease = disease[~disease['Ontology ID'].isin(drop_terms)]
    disease_descendants = []
    for i, row in disease.iterrows():
        descendants = get_descendants(mondo, row['Ontology ID'], names = True, direct_only= False)
        descendants['mondo_ancestor_id'] = row['Ontology ID']
        descendants['ancestor_label'] = row['Name']
        disease_descendants.append(descendants)

    disease_descendants = pd.concat(disease_descendants, ignore_index=True)
    disease_descendants = disease_descendants.rename(columns = {'Ontology ID': 'mondo_disease_id',
                                                                'Name': 'disease_label'})
    return disease_descendants[['mondo_disease_id', 'mondo_ancestor_id', 'ancestor_label']]

def main():
    ###### change these file paths!!!! #########
    clingen = load_clingen_data('data/rawdata/Clingen-Gene-Disease-Summary-2025-08-20.csv')
    print(clingen)
    ensembl = collate_ensembl_data('data/rawdata/ensembl/', 'Homo_sapiens.GRCh38.114')
    print(ensembl)
    ############################################

    #match clingen and ensembl
    clingen = clingen.merge(ensembl, on = 'gene_name', how = 'left')

    ###### check the excluded terms here - they're pretty arbitrary ####
    human_disease_descendants = get_mondo_descendants()
    ####################################################################

    clingen = clingen.merge(human_disease_descendants, on = 'mondo_disease_id', how = 'left')

    clingen['case/control'] = 'control'
    clingen.loc[clingen['classification'].isin(['Definitive', 'Strong', 'Moderatre']), 'case/control'] = 'case'
    clingen.loc[clingen['classification'].isin(['Limited']), 'case/control'] = None


    clingen.to_csv('data/clingen.formatted.txt', sep = '\t')

    clingen[['mondo_ancestor_id', 'ancestor_label']].drop_duplicates(keep = 'first').to_csv('data/ontology_mapping.starter.txt', sep = '\t')

if __name__ == "__main__":
    main()

