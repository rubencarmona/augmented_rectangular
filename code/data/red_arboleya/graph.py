import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import json

import os
#Loading data
cableimpedances = pd.read_csv("cableimpedances.csv")
for i in os.listdir():
    print(i)
    if "ct-65082" not in i: continue
    if "ct" in i:
        with open(os.path.join(i, "net.json"), "r") as f:
            net = json.load(f)
        data = pd.DataFrame(net["network"]["branch"]).T
        buses = pd.DataFrame(net["network"]["bus"]).T
        
        #buses.reset_index(inplace=True)
        #loads = pd.read_csv(os.path.join(i, "loads.csv"))
        #pcrs = data[["nodeto", "PCR"]].drop_duplicates()
        #pcrsdict = pcrs.set_index("nodeto").to_dict()
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
        coloredge = []
        for _, r in data.iterrows():
            edge = (r['nodefrom'],r['nodeto'])
            G.add_edge(*edge)
            if cableimpedances.loc[cableimpedances["code"]==r["type"]]["threephasecable"].values[0]:
                coloredge.append("blue")
            else:
                coloredge.append("green")

        color = []
        nodesize = []
        for n in G.nodes():
            if buses.iloc[n]["slack"]:
                color.append("orange")
                nodesize.append(60)
            elif buses.iloc[n]["load"]:
                color.append("red")
                nodesize.append(20)
            else:
                color.append("black")
                nodesize.append(10)
        unindG = G.to_undirected()

        #Plotting graph
        fig, ax1 = plt.subplots(figsize=(8,8))
        nx.draw_kamada_kawai(unindG,with_labels=False, node_size=nodesize, node_color= color, edge_color=coloredge, linewidths=2, width=1, font_size=12, ax=ax1)
        fig.savefig(os.path.join(i, "grafonew.pdf"), dpi=300, bbox_inches='tight')
            