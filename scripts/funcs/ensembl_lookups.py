import pandas as pd
import re

def parse_attributes(attribute):
    # Regular expression to extract key-value pairs
    pattern = re.compile(r'(\S+) "([^"]+)"')
    matches = pattern.findall(attribute)
    return {key: value for key, value in matches}

def gtf_to_txt(ensembl_data, chunksize = 10000):
    data_header = ['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attribute']

    processed_chunks = []

    # Read the Ensembl gene information in chunks
    for chunk in pd.read_csv(ensembl_data, names=data_header, sep='\t', skiprows=5, chunksize=chunksize):
        # Apply the function to the attribute column
        attributes_df = chunk['attribute'].apply(parse_attributes).apply(pd.Series)

        # Merge the new columns with the original DataFrame
        chunk = pd.concat([chunk, attributes_df], axis=1)

        # Drop the original attribute column
        chunk.drop(columns=['attribute'], inplace=True)

        # Filter rows where feature is 'gene'
        chunk = chunk[chunk['feature'] == 'gene']

        # Select the specified columns
        chunk = chunk[['seqname', 'start', 'end', 'strand', 'gene_id', 'gene_name', 'gene_biotype']]
        chunk = chunk.loc[chunk['gene_biotype'] == 'protein_coding']
        chunk = chunk.drop(columns = 'gene_biotype')
        chunk = chunk.rename(columns = {'seqname':'chromosome'})

        # Append the processed chunk to the list
        processed_chunks.append(chunk)

        # Concatenate all processed chunks
        ensembl_info = pd.concat(processed_chunks, ignore_index=True)

    return ensembl_info

def get_canonical_transcripts(canonical_data, df):
    
    canonical_info = pd.read_csv(canonical_data, names = ['gene_id','transcript_id','notes'] , sep = '\t')
    canonical_info = canonical_info[['gene_id', 'transcript_id']]

    canonical_info['gene_id'] = canonical_info['gene_id'].str.split('.').str[0]
    canonical_info['transcript_id'] = canonical_info['transcript_id'].str.split('.').str[0]

    df = pd.merge(df, canonical_info, on = 'gene_id', how = 'left')

    return df

def get_protein_information(protein_data, df, canonical_only = True):
    
    protein_info = pd.read_csv(protein_data, sep = '\t')
    #Keep only SWISSPROT IDs
    protein_info = protein_info.loc[protein_info['db_name'] == 'Uniprot/SWISSPROT']

    protein_info = protein_info.rename(columns = {'gene_stable_id':'gene_id',
                                                  'transcript_stable_id':'transcript_id',
                                                  'protein_stable_id':'protein_id',
                                                  'xref':'uniprot_id'})
    
    protein_info = protein_info[['gene_id', 'transcript_id', 'protein_id', 'uniprot_id']]
    print(protein_info)
    
    if canonical_only == True:
        df = pd.merge(df, protein_info, on = ['gene_id', 'transcript_id'], how = 'left')
    else:
        df = pd.merge(df, protein_info, on = 'gene_id', how = 'left')

    return df

def get_entrez_ids(entrez_data, df):
    
    entrez_info = pd.read_csv(entrez_data, sep = '\t')

    entrez_info = entrez_info.rename(columns = {'gene_stable_id':'gene_id',
                                                  'xref':'entrez_id'})
    
    entrez_info = entrez_info[['gene_id', 'entrez_id']].drop_duplicates(keep = 'first')
    
    df = pd.merge(df, entrez_info, on = 'gene_id', how = 'left')

    return df

