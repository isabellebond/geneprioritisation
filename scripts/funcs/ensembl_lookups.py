import pandas as pd
import re

def get_canonical_transcripts(canonical_data, df):
    
    canonical_info = pd.read_csv(canonical_data, names = ['gene_id','transcript_id','notes'] , sep = '\t')
    canonical_info = canonical_info[['gene_id', 'transcript_id']]

    canonical_info['gene_id'] = canonical_info['gene_id'].str.split('.').str[0]
    canonical_info['transcript_id'] = canonical_info['transcript_id'].str.split('.').str[0]

    df = pd.merge(df, canonical_info, on = 'gene_id', how = 'left')

    return df


def get_entrez_ids(entrez_data, df):
    
    entrez_info = pd.read_csv(entrez_data, sep = '\t')

    entrez_info = entrez_info.rename(columns = {'gene_stable_id':'gene_id',
                                                  'xref':'entrez_id'})
    
    entrez_info = entrez_info[['gene_id', 'entrez_id']].drop_duplicates(keep = 'first')
    
    df = pd.merge(df, entrez_info, on = 'gene_id', how = 'left')

    return df

