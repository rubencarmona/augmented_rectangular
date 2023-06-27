import pandas as pd
import numpy as np

import sys

import json
import os

with open(os.path.join("input.json"), "r") as f:
    df = json.load(f)

cables = pd.DataFrame.from_dict(df["network"]["branches"]).T
cables = cables[cables.columns[3:-3]]
cables.drop_duplicates(inplace=True)
cables.reset_index(drop=True, inplace=True)
cables["alias"] = "CUERVA-"+cables.index.astype(str)

zb = ((400/np.sqrt(3))**2)/(df["configuration"]["sbase"])

cableparameters = {}
for _, r in cables.iterrows():
    cableparameters[r["alias"]] = {}
    cableparameters[r["alias"]]["real"] = [[r["r_f"]*zb, r["r_ff"]*zb, r["r_ff"]*zb, r["r_fn"]*zb],
                                           [r["r_ff"]*zb, r["r_f"]*zb, r["r_f"]*zb, r["r_fn"]*zb],
                                           [r["r_ff"]*zb, r["r_ff"]*zb, r["r_f"]*zb, r["r_fn"]*zb],
                                           [r["r_ff"]*zb, r["r_ff"]*zb, r["r_ff"]*zb, r["r_n"]*zb]]
    cableparameters[r["alias"]]["image"] = [[r["x_f"]*zb, r["x_ff"]*zb, r["x_ff"]*zb, r["x_fn"]*zb],
                                           [r["x_ff"]*zb, r["x_f"]*zb, r["x_f"]*zb, r["x_fn"]*zb],
                                           [r["x_ff"]*zb, r["x_ff"]*zb, r["x_f"]*zb, r["x_fn"]*zb],
                                           [r["x_ff"]*zb, r["x_ff"]*zb, r["x_ff"]*zb, r["x_n"]*zb]]
with open(os.path.join("cableparameters.json"), "w") as f:
    json.dump(cableparameters,f)
sys.exit()
for i in df["network"]["branches"]:
    n = df["network"]["branches"][i]
    c = cables.loc[((cables["r_f"]==n["r_f"]) & (cables["x_f"]==n["x_f"]) & (cables["r_ff"]==n["r_ff"]))]["alias"].values[0]
    df["network"]["branches"][i]["alias"] = c

with open(os.path.join("input.json"), "w") as f:
    json.dump(df,f)

# net.json
net = {}
net["network"] = {}
net["network"]["bus"] = {}
net["network"]["branch"] = {}

for i in df["network"]["nodes"]:
    j = str(int(i)-1)
    net["network"]["bus"][j] = {}
    if df["network"]["nodes"][i]["type"] == "heading":
        slack = True
        load = False
    elif df["network"]["nodes"][i]["type"] == "transit":
        slack = False
        load = False
    elif df["network"]["nodes"][i]["type"] == "load":
        slack = False
        load = True

    net["network"]["bus"][j]["slack"] = slack
    net["network"]["bus"][j]["load"] = load
    net["network"]["bus"][j]["name"] = df["network"]["nodes"][i]["id"]
    net["network"]["bus"][j]["type"] = "real-cuerva"

for i in df["network"]["branches"]:
    j = str(int(i)-1)
    net["network"]["branch"][j] = {}

    net["network"]["branch"][j]["type"] = df["network"]["branches"][i]["alias"]
    net["network"]["branch"][j]["nodefrom"] = int(int(df["network"]["branches"][i]["node_in"])-1)
    net["network"]["branch"][j]["nodeto"] = int(int(df["network"]["branches"][i]["node_out"])-1)
    net["network"]["branch"][j]["length"] = 1.0

with open(os.path.join("net.json"), "w") as f:
    json.dump(net,f)

# imbalance.json
imbalance = {}
for i in df["measurements"]["p_inj"]:
    sb = df["configuration"]["sbase"]
    l = df["network"]["nodes"][i]["id"]
    if df["network"]["nodes"][i]["type"] == "heading": continue
    p = df["measurements"]["p_inj"]
    q = df["measurements"]["q_inj"]
    imbalance[l] = {}
    imbalance[l]["p"] = [p[i]["1"]["value"]*sb,p[i]["2"]["value"]*sb,p[i]["3"]["value"]*sb]
    imbalance[l]["q"] = [q[i]["1"]["value"]*sb,q[i]["2"]["value"]*sb,q[i]["3"]["value"]*sb]
with open(os.path.join("imbalance.json"), "w") as f:
    json.dump(imbalance,f)