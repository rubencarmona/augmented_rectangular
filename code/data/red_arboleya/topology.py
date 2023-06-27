import pandas as pd
import numpy as np

import json

import networkx

import os


path_arboleya = os.path.join('..', '..', '..', '..', 'Paper y Red Arboleya', 'Sim_files_190128_OK_V0', 'GIS_data')

cts = pd.read_excel(os.path.join(path_arboleya, "master.xlsx"), sheet_name="CT - TRAFO")
lbts = pd.read_excel(os.path.join(path_arboleya, "master.xlsx"), sheet_name="Linea BT")
tramos = pd.read_excel(os.path.join(path_arboleya, "master.xlsx"), sheet_name="Segmento BT")
acometidas = pd.read_excel(os.path.join(path_arboleya, "master.xlsx"), sheet_name="Acometidas")
coordenadas_seg = pd.read_excel(os.path.join(path_arboleya, "master.xlsx"), sheet_name="Coordenadas Segmentos")

loads = pd.read_excel(os.path.join(path_arboleya, "load.xlsx"), sheet_name="Load")
phase = pd.read_excel(os.path.join(path_arboleya, "phase meters.xlsx"))
loadphase = loads[["ID", "PCR"]].merge(phase[["ID", "Fase"]], on="ID", how="inner")

ctlist = cts["Mslink CT"].drop_duplicates().tolist()
ctnodes = cts["NUDO CELDA TRAFO"].drop_duplicates().tolist()

#coordenadas_seg = coordenadas_seg[["Mslink", "Longitud"]].drop_duplicates()

nodesdict = {}
for _, i in enumerate(ctlist):
    print("CT {}".format(i))
    ctcomplete = pd.DataFrame()
    if i == 65043: continue
    ctmsk = i
    ctnode = ctnodes[_]
    lbtlist = lbts.loc[lbts["Mslink CT"]==ctmsk][["Mslink linea", "NE"]].set_index("Mslink linea").rename({"NE":"lineas"}, axis=1).to_dict()
    for j in lbtlist["lineas"]:
        segments = tramos.loc[tramos["Mslink linea"] == j]
        #segments_length = segments.merge(coordenadas_seg, left_on="Mslink", right_on="Mslink", how="left")
        cabletypes = segments["Tipo Cable"].tolist()
        cablelength = segments["Longitud"].tolist()
        if len(segments)>1: 
            totalnodes = list(pd.concat([segments["Nudo Origen"].drop_duplicates(), segments["Nudo Destino"].drop_duplicates()]).drop_duplicates())
            G = networkx.Graph()
            G.add_nodes_from(totalnodes)
            edges = list(tuple(sub) for sub in segments[["Nudo Origen", "Nudo Destino"]].values.tolist())
            edges = edges+[(ctnode,lbtlist["lineas"][j])]
            cabletypes += ["BT - Desconocido BT"]
            cablelength += [1]
            attrs = {}
            for __, k in enumerate(edges):
                attrs[k] = {}
                attrs[k]["cable"] = cabletypes[__]
                attrs[k]["length"] = cablelength[__]
            G.add_edges_from(edges)
            networkx.set_edge_attributes(G, attrs)
            newG = list(networkx.bfs_edges(G,ctnode))
            cs = []
            ln = []
            for l in newG:
                cs.append(G[l[0]][l[1]]["cable"])
                ln.append(G[l[0]][l[1]]["length"])
            newtramos = pd.DataFrame(list(networkx.bfs_edges(G,ctnode)), columns=["nodefrom", "nodeto"])
            newtramos["cable"] = cs
            newtramos["length"] = ln

            lbtcomplete = newtramos.merge(acometidas[["Nudo Origen", "Clave BDI"]].rename({"Nudo Origen":"nodeto", "Clave BDI":"PCR"}, axis=1), left_on="nodeto", right_on="nodeto", how="left")

            ctcomplete = pd.concat([ctcomplete, lbtcomplete], axis=0)
            ctcomplete["PCR"] = ctcomplete["PCR"].fillna(0)
            ctcomplete["PCR"] = ctcomplete["PCR"].astype(int)
    
    nodescomplete = pd.DataFrame({"nodes":list(pd.concat([ctcomplete["nodefrom"].drop_duplicates(), ctcomplete["nodeto"].drop_duplicates()], axis=0).drop_duplicates())})
    nodescomplete["type"] = "transit"
    nodescomplete.loc[nodescomplete["nodes"]==ctnode, "type"] = "slack"

    pcrs = pd.DataFrame({"nodes":ctcomplete["PCR"].dropna().drop_duplicates().tolist()})
    pcrs["type"] = "load"

    loadscts = loadphase.loc[loadphase["PCR"].isin(pcrs["nodes"].tolist())]
    
    nodescomplete = pd.concat([nodescomplete,pcrs], axis=0)
    nodescomplete.reset_index(drop=True, inplace=True)

    if not os.path.exists(os.path.join("ct-{}".format(i))): os.makedirs(os.path.join("ct-{}".format(i)))

    ctcomplete.to_csv(os.path.join("ct-{}".format(i), "branches.csv"), index=False)
    nodescomplete.to_csv(os.path.join("ct-{}".format(i), "nodes.csv"), index=False)
    loadscts.to_csv(os.path.join("ct-{}".format(i), "loads.csv"), index=False)

    #break