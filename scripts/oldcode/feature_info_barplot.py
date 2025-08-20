import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.ticker import MaxNLocator

mondo_ancestors = pd.read_csv('data/ontologymapping/mondo.humandisease.clingen.txt', sep = '\t', index_col  = 'mondo_ancestor_id')

clingen = pd.read_csv('data/formatteddata/clingen.gene_disease.txt', sep = '\t')
chembl = pd.read_csv('data/features/formatted/chembl.txt', sep = '\t')
mouse = pd.read_csv('data/features/formatted/mouse.txt', sep = '\t')
proteinexpression = pd.read_csv('data/features/formatted/proteinexpression.txt', sep = '\t')
rnaspecificity = pd.read_csv('data/features/formatted/rnaspecificity.txt', sep = '\t')
proteinlinks = pd.read_csv('data/features/formatted/proteinlinks.txt', sep = '\t')

datasets = {
            'clinical trial':chembl, 
            'mouse knockout': mouse, 
            'protein expression': proteinexpression, 
            'rna expression': rnaspecificity,
            'protein links': proteinlinks
            }

columnofinterest = {
                    'clinical trial':['max_trial_phase', 3],
                    'mouse knockout':['ontology_ancestor_id',0],
                    'protein expression':['protein.level', 3],
                    'rna expression': ['rna.zscore', 0.674],
                    'protein links': ['experimental', 700]
                    }

counts = clingen
counts = clingen.drop_duplicates(subset = ['gene_id','mondo_ancestor_id'], keep = 'first')
counts['clingen assertion'] = 1
counts = counts.groupby(['mondo_ancestor_id']).sum().reset_index()
counts = counts[['mondo_ancestor_id', 'clingen assertion']].set_index('mondo_ancestor_id')



for name, dataset in datasets.items():
    df = dataset
    df['count'] = 1
    df[name] = 0
    df = df.sort_values(by = columnofinterest[name][0], ascending=False)
    df = dataset.drop_duplicates(subset = ['gene_id','mondo_ancestor_id'], keep = 'first')
    if not name in ['mouse knockout']:
        print(columnofinterest[name][0])
        df.loc[df[columnofinterest[name][0]] >= columnofinterest[name][1], name] = 1
    else:
        df[name] = 1
    df = df.groupby(['mondo_ancestor_id']).sum().reset_index()
    df = df[['mondo_ancestor_id', name]].set_index('mondo_ancestor_id')

    counts = counts.join(df, how = 'outer')
    

counts = counts.sort_values(by = ['clingen assertion'], ascending=False)
counts = counts.fillna(0)
counts = counts.astype(int)

counts = counts.join(mondo_ancestors, how = 'inner').set_index('ancestor_label')
print(counts)

# Define number of rows and columns
fig, axes = plt.subplots(nrows=3, ncols=9, figsize=(20, 10), sharex = True)
palette = sns.color_palette("pastel", len(counts.columns))
axes = axes.flatten()

# Create bar plots
for i, (row_name, row_data) in enumerate(counts.iterrows()):
    print(row_name, row_data)
    ax = axes[i]
    ax.bar(row_data.index, row_data.fillna(0), color = palette)

    row_name = row_name.split(' ')
    row_name = " ".join(
    word + ("\n" if (i + 1) % 2 == 0 and i + 1 < len(row_name) else "")
    for i, word in enumerate(row_name)
    )
    ax.set_title(row_name, fontsize=8, fontweight = 'bold')
    #ax.set_xticklabels(row_data.index, rotation=90, fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    if i < 9:
        ax.set_ylim(0, 1015)
    elif i < 18:
        ax.set_ylim(0, 170)
    else:
        ax.set_ylim(0, 40)
        ax.set_xticklabels(['clingen assertion', 'clinical trial', 'mouse knockout', 'protein expression', 'rna expression', 'protein links'], rotation=50, ha='right', fontsize=8)
    #ax.locator_params(axis = 'y', nbins = 5)
    # Get current y-ticks and filter only integer values
    y_ticks = ax.get_yticks()
    y_ticks_int = [int(tick) for tick in y_ticks if tick.is_integer()]  # Keep only integers

    # Set the integer y-tick labels with fontsize 8
    ax.set_yticks(y_ticks_int)
    ax.set_yticklabels(y_ticks_int, fontsize=8)

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

#
# Adjust Layout
plt.subplots_adjust(wspace=0.1, hspace=0.5)  # Adjust horizontal and vertical spacing
plt.tight_layout()
plt.savefig('data/figures/feature_info_barplot_experimental.png', dpi=300)
plt.show()