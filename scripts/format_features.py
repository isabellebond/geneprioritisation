import pandas as pd
from funcs.data_formatting import mondo_to_ontology, ontology_to_disease_gene, read_and_explode_chembl, read_and_explode_opentargets, format_protein_data
import os
import ast

data = os.path.join('data')
features = os.path.join(data, 'features')
ontologies = os.path.join(data, 'ontologymapping')

clingen_df = pd.read_csv('data/formatteddata/clingen.gene_disease.txt', sep = '\t')
mapper = pd.read_csv(os.path.join(ontologies, 'between.ontologies.txt'), sep = '\t')

#Add mouse data
mouse_df = pd.read_csv(os.path.join(features, 'unformatted', 'opentargets','mousePhenotypes.csv'))
mouse_ont = pd.read_csv(os.path.join(ontologies, 'mp.mammilianphenotype.clingen.txt'), sep = '\t')
mouse_desc = pd.read_csv(os.path.join(ontologies, 'mp.mammilianphenotype.descendants.txt'), sep = '\t')

mouse_mapper = mondo_to_ontology(mapper, mouse_desc, 'mp')
mouse_df = ontology_to_disease_gene(clingen_df, mouse_mapper, mouse_df, phenotype_id = 'modelPhenotypeId', gene_id = 'targetFromSourceId')
mouse_df.to_csv(os.path.join(features, 'formatted', 'mouse.txt'), sep = '\t', index = False)
mouse_df['has_mouse_phenotype'] = 1

#Add human drug data
drug_df = pd.read_csv(os.path.join(features, 'unformatted', 'opentargets','chembl.csv'))
efo_ont = pd.read_csv(os.path.join(ontologies, 'efo.measurement.clingen.txt'), sep = '\t')
efo_desc = pd.read_csv(os.path.join(ontologies, 'efo.measurement.descendants.txt'), sep = '\t')
hp_ont = pd.read_csv(os.path.join(ontologies, 'hp.phenotypicabnormality.clingen.txt'), sep = '\t')
hp_desc = pd.read_csv(os.path.join(ontologies, 'hp.phenotypicabnormality.descendants.txt'), sep = '\t')
mondo_ont = pd.read_csv(os.path.join(ontologies, 'mondo.humandisease.clingen.txt'), sep = '\t')
mondo_desc = pd.read_csv(os.path.join(ontologies, 'mondo.humandisease.descendants.txt'), sep = '\t')

efo_mapper = mondo_to_ontology(mapper, efo_desc, 'efo')
hp_mapper = mondo_to_ontology(mapper, hp_desc, 'hp')
mondo_mapper = mondo_to_ontology(mapper, mondo_desc, 'mondo')
ont_mapper = pd.concat([efo_mapper, hp_mapper, mondo_mapper], axis = 0, ignore_index=True)

chembl_df = read_and_explode_chembl(os.path.join(features, 'unformatted', 'opentargets','chembl.csv'))

chembl_df = ontology_to_disease_gene(clingen_df, ont_mapper, chembl_df, phenotype_id = 'ontology_id', gene_id = 'gene_id', value = True, value_id='max_trial_phase')
chembl_df.to_csv(os.path.join(features, 'formatted', 'chembl.txt'), sep = '\t', index = False)

#Add tissue expression data
opentargets_rnavalue = read_and_explode_opentargets(os.path.join(features, 'unformatted', 'opentargets','baselineExpression.csv'), 'rna.value', mapper, clingen_df)
opentargets_rnavalue.to_csv(os.path.join(features, 'formatted', 'rnaexpression.txt'), sep = '\t', index = False)

opentargets_proteinvalue = read_and_explode_opentargets(os.path.join(features, 'unformatted', 'opentargets','baselineExpression.csv'), 'protein.level', mapper, clingen_df)
opentargets_proteinvalue.to_csv(os.path.join(features, 'formatted', 'proteinexpression.txt'), sep = '\t', index = False)

opentargets_rnaspecificity = read_and_explode_opentargets(os.path.join(features, 'unformatted', 'opentargets','baselineExpression.csv'), 'rna.zscore', mapper, clingen_df)
opentargets_rnaspecificity.to_csv(os.path.join(features, 'formatted', 'rnaspecificity.txt'), sep = '\t', index = False)

#Add protein data
protein_df = format_protein_data(os.path.join(features, 'unformatted', '9606.protein.physical.links.detailed.v12.0.txt'), clingen_df)
