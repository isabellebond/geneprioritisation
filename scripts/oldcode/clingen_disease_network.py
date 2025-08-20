import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import numpy as np

clingen = pd.read_csv('data/formatteddata/clingen.gene_disease.txt', sep = '\t')
clingen = clingen.drop_duplicates(subset = ['mondo_disease_id','ancestor_label'], keep = 'first')
data = clingen[['mondo_disease_id', 'ancestor_label']].copy()
data['ancestor_label'] = data['ancestor_label'].str.replace(' ','\n')

# Group by disease and get sets of ancestors
disease_to_ancestors = data.groupby('mondo_disease_id')['ancestor_label'].apply(set)

# Create a dictionary to store edge weights
edge_weights = {}

# Iterate over diseases and find ancestor pairs
for ancestors in disease_to_ancestors:
    for pair in combinations(ancestors, 2):  # Get all pairs of ancestors per disease
        edge_weights[pair] = edge_weights.get(pair, 0) + 1  # Increase weight by 1 per shared disease

# Create the graph
G = nx.Graph()

# Add edges with weights
for (a1, a2), weight in edge_weights.items():
    G.add_edge(a1, a2, weight=np.log(weight + 1))
G.remove_nodes_from(list(nx.isolates(G)))
# Positioning using spring layout
pos = nx.spring_layout(G, seed = 42, k = 3, weight = 'weights')

# Extract edge weights for visualisation
edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())

# Draw the network
plt.figure(figsize=(12, 12))


nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")

# Draw edges with transparency (alpha=0.2)
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='grey', width=[w  for w in weights], alpha=0.5)



# Draw edge labels (weights)
#edge_labels = {edge: weight for edge, weight in edge_weights.items()}
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
plt.tight_layout()
plt.title("Ancestor Network (Edges Weighted by Shared Diseases)")
plt.show()