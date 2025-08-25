import pandas as pd
import numpy as np

from funcs.data import read_parquet_files
from funcs.ontologies import load_ontology, get_descendants

def get_opentargets_l2g(study_type='gwas', drop_duplicates = True):

    #get GWAS loci
    gwas = read_parquet_files('data/opentargets/study/study', primary_filter_id='studyType', primary_filter=[study_type])
    
    study_ids = gwas['studyId'].unique().tolist()
    
    gwas_loci = read_parquet_files('data/opentargets/credible_set/credible_set', primary_filter_id='studyId', primary_filter = study_ids)

    gwas = gwas.merge(gwas_loci[['studyId', 'studyLocusId']], on='studyId', how='right')

    #get coloc results
    locus2gene = read_parquet_files('data/opentargets/l2g_predictor/l2g_prediction')

    gwas = gwas[['studyId', 'studyLocusId', 'pubmedId', 'diseaseIds']]
    gwas['diseaseId'] = gwas['diseaseIds'].apply(lambda x: x[0] if isinstance(x, (list, np.ndarray)) and len(x) > 0 else np.nan)
    locus2gene = locus2gene[['studyLocusId', 'geneId', 'score']]

    locus2gene = locus2gene.merge(gwas, on='studyLocusId', how='left')

    locus2gene = locus2gene.rename(columns={'studyLocusId':'locus_id', 
                                            'geneId':'gene_id', 
                                            'score':'l2g_score',
                                            'diseaseId':'gwas_id_efo',})

    return locus2gene
    
def get_ancestors():
    ontology_lookup = pd.read_csv('data/ontology_mapping.manualedits.txt', sep='\t')

    onto, efo = load_ontology('http://www.ebi.ac.uk/efo/releases/v3.81.0/efo.owl', 'http://www.ebi.ac.uk/efo/')
    efo_terms = []
    for i,row in ontology_lookup.iterrows():
        id = row['efo_ancestor_id']
        label = row['efo_ancestor_label']
         #skip if nan
        # Skip if missing or blank
        if pd.isna(id) or id.strip() == '' or id.lower() == 'nan':
            continue
        if id.startswith('MONDO'):
            term = get_descendants(onto, efo, id, prefix = 'efo.', alternate_iri='http://purl.obolibrary.org/obo/')
        else:
            term = get_descendants(onto, efo, id, prefix = 'efo.')
        term['efo_ancestor_id'] = id
        term['efo_ancestor_label'] = label
        term.to_csv(f'data/ontology_lookups/efo/{id}.txt', sep='\t', index=False)
        efo_terms.append(term)

    efo_terms = pd.concat(efo_terms, ignore_index=True)

    efo_terms = efo_terms.rename(columns={'Ontology ID':'gwas_id_efo', 'Name':'gwas_label'})
    return efo_terms
    

def main():
    efo_terms = get_ancestors()
    l2g = get_opentargets_l2g(study_type='gwas', drop_duplicates=True)

    efo_terms = efo_terms.merge(l2g, on = 'gwas_id_efo', how='right')
    efo_terms.dropna(subset=['efo_ancestor_id', 'efo_ancestor_label'], inplace=True)
    efo_terms.to_csv('data/opentargets_formatted/l2g.txt', sep='\t', index=False)
    
     #get clingen genes
    clingen = pd.read_csv('data/clingen.formatted.txt', sep='\t')
    ontology_lookup = pd.read_csv('data/ontology_mapping.manualedits.txt', sep='\t')
    clingen = clingen.drop_duplicates(subset=['gene_id', 'mondo_disease_id', 'mondo_ancestor_id'])
    clingen = clingen.merge(ontology_lookup, on='mondo_ancestor_id', how='left')

    clingen = clingen[['gene_id', 'gene_name', 'disease_label', 'mondo_disease_id', 'efo_ancestor_id', 'efo_ancestor_label']]

    clingen = clingen.merge(efo_terms, on = ['gene_id', 'efo_ancestor_label', 'efo_ancestor_id'], how='left')
    
    clingen['gwas_association'] = np.where(clingen['l2g_score'] > 0.5, True, False)
    clingen = clingen.drop_duplicates(subset=['gene_id', 'gene_name', 'disease_label', 'mondo_disease_id', 'efo_ancestor_id', 'efo_ancestor_label', 'gwas_id_efo'])

    clingen = clingen.groupby(
    ['gene_id', 'gene_name', 'disease_label', 'mondo_disease_id', 'efo_ancestor_id', 'efo_ancestor_label']
    ).agg(
        gwas_association=('gwas_association', 'max'),
        gwas_id_efo=('gwas_id_efo', lambda x: ';'.join(x.dropna().unique())),
        gwas_label=('gwas_label', lambda x: ';'.join(x.dropna().unique())),
        l2g_score=('l2g_score', lambda x: ';'.join(map(str, x.dropna().unique())))
    ).reset_index()

    
    clingen.to_csv('data/features/gwas_l2g.txt', sep='\t', index=False)


if __name__ == "__main__":
    main()