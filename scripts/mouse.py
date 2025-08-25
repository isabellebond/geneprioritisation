import pandas as pd
import numpy as np

from funcs.data import read_parquet_files
from funcs.ontologies import load_ontology, get_descendants

def get_opentargets_mouse():

    #get GWAS loci
    clingen = pd.read_csv('data/clingen.formatted.txt', sep='\t')
    mouse = read_parquet_files('data/opentargets/mouse_phenotype') #, primary_filter_id='targetFromSourceId', primary_filter = clingen['gene_id'].values.tolist())
    mouse = mouse.loc[mouse['targetFromSourceId'].isin(clingen['gene_id'].values.tolist())]
    mouse = mouse.rename(columns={'targetFromSourceId':'gene_id',
                                  'modelPhenotypeId':'mp_id',
                                  'targetInModelEnsemblId':'gene_id_mouse'})
    
    mouse = mouse[['gene_id', 'gene_id_mouse', 'mp_id']]
    mouse['mp_id'] = mouse['mp_id'].str.replace(':', '_')
    print(mouse)
    return  mouse

def get_ancestors():
    ontology_lookup = pd.read_csv('data/ontology_mapping.manualedits.txt', sep='\t')

    onto, mp = load_ontology('http://purl.obolibrary.org/obo/mp/mp-international.owl', 'http://purl.obolibrary.org/obo/')
    mp_terms = []
    for i,row in ontology_lookup.iterrows():
        id = row['mp_ancestor_id']
        id = id.split('; ')
        if len(id) > 1:
            for i in range(len(id)):
                label = row['mp_ancestor_label'].split('; ')[i]
                 #skip if nan
                # Skip if missing or blank
                if pd.isna(id[i]) or id[i].strip() == '' or id[i].lower() == 'nan':
                    continue
                else:
                    term = get_descendants(onto, mp, id[i], prefix = 'obo.')
                term['mp_ancestor_id'] = id[i]
                term['mp_ancestor_label'] = label
                term.to_csv(f'data/ontology_lookups/mp/{id[i]}.txt', sep='\t', index=False)
                mp_terms.append(term)
        else:
            id = id[0]
            label = row['mp_ancestor_label']
            #skip if nan
            # Skip if missing or blank
            if pd.isna(id) or id.strip() == '' or id.lower() == 'nan':
                continue
            else:
                term = get_descendants(onto, mp, id, prefix = 'obo.')
            term['mp_ancestor_id'] = id
            term['mp_ancestor_label'] = label
            term.to_csv(f'data/ontology_lookups/mp/{id}.txt', sep='\t', index=False)
            mp_terms.append(term)

    mp_terms = pd.concat(mp_terms, ignore_index=True)

    mp_terms = mp_terms.rename(columns={'Ontology ID':'mp_id', 'Name':'mp_label'})
    return mp_terms

def main():
    clingen = pd.read_csv('data/clingen.formatted.txt', sep='\t')
    ontology_lookup = pd.read_csv('data/ontology_mapping.manualedits.txt', sep='\t')
    clingen = clingen.merge(ontology_lookup, on='mondo_ancestor_id', how='left')

    mp_terms = get_ancestors()
    print(mp_terms)
    mouse = get_opentargets_mouse()
    mouse = mouse.merge(mp_terms, on='mp_id', how='left')
    print(mouse)

    mouse = mouse.merge(clingen, on=['gene_id', 'mp_ancestor_id', 'mp_ancestor_label'], how='right')
    mouse = mouse[['gene_id', 'gene_name', 'disease_label','mondo_disease_id', 'gene_id_mouse', 'mp_id', 'mp_label', 'mp_ancestor_id', 'mp_ancestor_label']]
    mouse = mouse.groupby(['gene_id', 'gene_name' , 'disease_label','mondo_disease_id','gene_id_mouse', 'mp_ancestor_id', 'mp_ancestor_label']).agg(
        mp_id = ('mp_id', lambda x: ';'.join(x.dropna().unique())),
        mp_label = ('mp_label', lambda x: ';'.join(x.dropna().unique()))
    ).reset_index()
    mouse['mouse_phenotype'] =  np.where(mouse['mp_id'].notna(), True, False)
    mouse.to_csv('data/features/mouse.txt', sep='\t', index=False)

if __name__ == "__main__":
    main()