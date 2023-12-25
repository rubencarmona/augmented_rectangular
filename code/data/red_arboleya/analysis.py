import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import json

import os

length = 0
n1f = 0
n3f = 0
counter = 0
nloads = 0

for i in os.listdir():
    if "ct" in i:
        
        if "imbalance.json" not in os.listdir(os.path.join(i)): continue
        counter += 1

        br = pd.read_csv(os.path.join(i, "branches.csv"))
        length += br["length"].sum()
        print("CT {}. Longitud: {}".format(i[2:], round(1e-3*br["length"].sum(), 2)))
        loads = pd.read_csv(os.path.join(i,"loads.csv"))
        nloads += len(loads)
        n3f += len(loads[((loads["Fase"]=="(Tri)") | (loads["Fase"]=="RST"))])
        n1f += len(loads)-len(loads[((loads["Fase"]=="(Tri)") | (loads["Fase"]=="RST"))])

print("Número de CTs alcanzados: {}".format(counter))
print("Longitud {} km".format(length*1e-3))
print("Numero de trifásicos: {}".format(n3f))
print("Numero de monofásicos: {}".format(n1f))
print("Numero de cargas: {}".format(nloads))