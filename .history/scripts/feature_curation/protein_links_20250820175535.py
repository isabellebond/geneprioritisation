import pandas as pd

def get_protein_links(path, clingen, strong_genes, experimental_protein_link_threshold=400):
    """
    Get protein links from a file and filter them based on strong genes from ClinGen data.
    
    Parameters:"""

    string = pd.read_csv(path, sep='\s+')
    print(string.head())
    string['protein1'] = string['protein1'].str.split('.').str[1]
    string['protein2'] = string['protein2'].str.split('.').str[1]
    string = string.merge(clingen[['gene_id', 'gene_name', 'protein_id']], left_on='protein1', right_on='protein_id', how='left')
    string.rename(columns = {'gene_id': 'linked_gene_id', 'gene_name': 'linked_gene_name', 'protein_id': 'linked_protein_id'}, inplace=True)
    string = string.merge(clingen[['gene_id', 'gene_name', 'protein_id']], left_on='protein2', right_on='protein_id', how='left')

    clingen['experimental_protein_link'] = False
    clingen['linked_protein_ids'] = None
    clingen['linked_protein_names'] = None
    clingen['evidence_strength'] = None

    for ancestor in clingen['mondo_ancestor_id'].unique():
        clingen_subset = clingen[clingen['mondo_ancestor_id'] == ancestor]
        strong_genes_subset = strong_genes[strong_genes['mondo_ancestor_id'] == ancestor]

        # Filter STRING interactions for the current ancestor
        string_subset = string[(string['linked_protein_id'].isin(strong_genes_subset['protein_id'])) &
                               (string['experimental'] > 0)]
        
        for i,row in clingen_subset.iterrows():
            gene_interactions = string_subset[string_subset['protein_id'] == row['protein_id']]

            if gene_interactions.empty:
                continue
            if gene_interactions['experimental'].max() < experimental_protein_link_threshold:
                clingen.loc[((clingen['gene_id'] == row['gene_id']) & (clingen['mondo_ancestor_id'] == ancestor)), 'experimental_protein_link'] = True
            clingen.loc[((clingen['gene_id'] == row['gene_id']) & (clingen['mondo_ancestor_id'] == ancestor)), 'linked_protein_ids'] = ';'.join(gene_interactions['linked_protein_id'].unique())
            clingen.loc[((clingen['gene_id'] == row['gene_id']) & (clingen['mondo_ancestor_id'] == ancestor)), 'linked_protein_names'] = ';'.join(gene_interactions['linked_gene_name'].unique())
            clingen.loc[((clingen['gene_id'] == row['gene_id']) & (clingen['mondo_ancestor_id'] == ancestor)), 'evidence_strength'] = ';'.join(gene_interactions['experimental'].astype(str).unique())
        
    
    return clingen


        

def main():
    clingen = pd.read_csv('data/clingen.formatted.txt', sep='\t')
    clingen_strong = clingen.loc[clingen['classification'].isin(['Definite', 'Strong', 'Moderate'])]
    cligen_strong = clingen_strong[['gene_id', 'gene_name', 'protein_id', 'mondo_disease_id', 'disease_label', 'mondo_mondo_ancestor_id', 'ancestor_label']].drop_duplicates()

    protein_links = get_protein_links('data/features/unformatted/9606.protein.links.detailed.v12.0.txt', cligen_strong, clingen)

    print(protein_links.head())
    protein_links.to_csv('data/features/protein_links.txt', sep='\t', index=False)


if __name__ == "__main__":
    main()