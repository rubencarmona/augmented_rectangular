import pandas as pd
import json
import sys, os

ct = "ct-65082"

nodes = pd.read_csv(os.path.join(ct, "nodes.csv"))
branches = pd.read_csv(os.path.join(ct, "branches.csv"))
nodetonewdict = {}
for _, r in branches.iterrows():
    if r["PCR"] != 0:
        nodetonewdict[r["nodeto"]] = r["PCR"]
    else:
        nodetonewdict[r["nodeto"]] = r["nodeto"]
for _, r in branches.iterrows():
    if r["nodefrom"] in nodetonewdict: continue
    nodetonewdict[r["nodefrom"]] = r["nodefrom"]
branches["nodefrom"] = branches["nodefrom"].apply(lambda x: nodetonewdict[x])
branches["nodeto"] = branches["nodeto"].apply(lambda x: nodetonewdict[x])
nodereduced = pd.DataFrame({"n": branches["nodefrom"].tolist()+branches["nodeto"].tolist()})
nodereduced = nodereduced["n"].drop_duplicates().tolist()
nodes = nodes.loc[nodes["nodes"].isin(nodereduced)]
nodes.reset_index(drop=True, inplace=True)
cables = pd.read_csv(os.path.join("cableimpedances.csv"))
cables["alias"] = cables["description"] + "-" + cables["kind"]
nodedict = {}
cabledict = dict(zip(cables["alias"], cables["code"]))
# net.json
net = {}
net["network"] = {}
net["network"]["bus"] = {}
net["network"]["branch"] = {}

for _, i in nodes.iterrows():
    j = str(_)
    net["network"]["bus"][j] = {}
    if i["type"] == "slack":
        slack = True
        load = False
    elif i["type"] == "transit":
        slack = False
        load = False
    elif i["type"] == "load":
        slack = False
        load = True
    nodedict[i["nodes"]] = j
    net["network"]["bus"][j]["slack"] = slack
    net["network"]["bus"][j]["load"] = load
    net["network"]["bus"][j]["name"] = str(i["nodes"])
    net["network"]["bus"][j]["type"] = "real-arboleya-{}".format(ct)

for _, i in branches.iterrows():
    #TODO: en qué unidades está la parametrización de cables de Arboleya
    j = str(_)
    net["network"]["branch"][j] = {}

    net["network"]["branch"][j]["type"] = cabledict[i["cable"]+"-"+i["kind"]]
    net["network"]["branch"][j]["nodefrom"] = int(nodedict[i["nodefrom"]])
    net["network"]["branch"][j]["nodeto"] = int(nodedict[i["nodeto"]])
    net["network"]["branch"][j]["length"] = 1 #i["length"] #TODO: NO ESTOY SEGURO DE ASIGNARLE SU LONGITUD O ON PORQUE NO SÉ SI ES UNITARIO

with open(os.path.join(ct,"net.json"), "w") as f:
    json.dump(net,f, indent=4)