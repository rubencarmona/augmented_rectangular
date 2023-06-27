import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import json

import os
#Loading data
for i in os.listdir():
    print(i)
    if "ct" in i:
        data = pd.read_csv(os.path.join(i, "branches.csv"))
        loads = pd.read_csv(os.path.join(i, "loads.csv"))
        pcrs = data[["nodeto", "PCR"]].drop_duplicates()
        pcrsdict = pcrs.set_index("nodeto").to_dict()
        #Parsing data
        nodes = []
        nodes.extend(data['nodefrom'].drop_duplicates().tolist())
        nodes.extend(data['nodeto'].drop_duplicates().tolist())
        nodesdata = pd.DataFrame({'nodes':nodes})
        nodesdata = nodesdata.drop_duplicates('nodes')
        nodes = nodesdata['nodes'].tolist()

        # Generating graph
        G=nx.DiGraph()
        G.add_nodes_from(nodes)

        #Adding edges to graph
        for _, r in data.iterrows():
            edge = (r['nodefrom'],r['nodeto'])
            G.add_edge(*edge)
        color = []
        for n in G.nodes():
            if n in pcrsdict["PCR"]:
                if pcrsdict["PCR"][n] in loads["PCR"].drop_duplicates().tolist():
                    color.append("red")
                else:
                    color.append("black")
            else:
                color.append("black")
        unindG = G.to_undirected()

        #Plotting graph
        fig, ax1 = plt.subplots(figsize=(20,20))
        nx.draw_kamada_kawai(unindG,with_labels=True, node_color = color, node_size=40, edge_color='black', linewidths=1, font_size=12, ax=ax1)
        fig.savefig(os.path.join(i,"grafo.pdf"), dpi=300)
    