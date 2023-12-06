import pandas as pd
import json
import numpy as np

import matplotlib.pyplot as plt
import graph
import sys, os


def plot_residuals(path_res, braz, us, cong, a, b, c):

    # Plot brazilian
    fig, ax = plt.subplots(figsize=(15,10))
    greater = 0
    for i in braz:
        if len(braz[i]["residuals"]) > greater: greater = len(braz[i]["residuals"])
        x = np.linspace(1,len(braz[i]["residuals"]),len(braz[i]["residuals"])).astype(int)
        y = braz[i]["residuals"]
        ax.plot(x, y, ls='-.', linewidth = 2.5, marker = 'o', color='grey')
    for i in us:
        if len(us[i]["residuals"]) > greater: greater = len(us[i]["residuals"])
        x = np.linspace(1,len(us[i]["residuals"]),len(us[i]["residuals"])).astype(int)
        y = us[i]["residuals"]
        ax.plot(x, y, ls='-.', linewidth = 2.5, marker = 'o', color='red', alpha=0.7)
    ax.set_xticks(np.linspace(1,greater,greater).astype(int))
    plt.yscale('log')
    ax.grid(True)
    ax.set_facecolor("gainsboro")
                
    ax.set_xticklabels(ax.get_xticks(),fontsize=15, fontname="Times New Roman")
    ax.set_yticklabels(ax.get_yticks(),fontsize=15, fontname="Times New Roman")
    ax.set_xlabel("Iterations", fontsize=12, fontname = "Times New Roman")
    ax.set_ylabel("Residuals", fontsize=15, fontname="Times New Roman")
    
    ax.set_title("Evolution of residual. Tolerance rate: 1e-4. Load: {}%. Imbalance ({}%,{}%,{}%)".format(100*round(cong, 2), a, b, c), fontsize=20, fontname="Times New Roman")
    #plt.show()
    fig.savefig(os.path.join(path_res, "residuals.png"), dpi=300)
    ax.plot(kind="line")



snom = pd.read_csv(os.path.join("data_original", "snominal.csv"))
res = {}
for p in os.listdir():
    if "ct-65046" not in p: continue
    if "results-us.json" not in os.listdir(os.path.join(p)): continue
    res[p] = {}

    with open(os.path.join(p, "results-us.json"), "r") as f:
        res[p]["us"] = json.load(f)
    with open(os.path.join(p, "results-brazilian.json"), "r") as f:
        res[p]["br"] = json.load(f)
    res[p]["voltages"] = pd.read_csv(os.path.join(p, "voltages.csv"))
    
    cups = pd.read_csv(os.path.join(p, "loads.csv"))
    cups3f = cups.loc[((cups["Fase"]=="RST") | (cups["Fase"]=="(Tri)"))]
    cups1f = cups.loc[((cups["Fase"]!="RST") & (cups["Fase"]!="(Tri)"))]
    res[p]["cups3f"] = len(cups3f)
    res[p]["cups1f"] = len(cups1f)

    with open(os.path.join(p, "imbalance.json"), "r") as f:
        res[p]["load"] = json.load(f)
    pR, pS, pT, qR, qS, qT = [], [], [], [], [], []
    for l in res[p]["load"]:
        pR.append(res[p]["load"][l]["p"][0])
        pS.append(res[p]["load"][l]["p"][1])
        pT.append(res[p]["load"][l]["p"][2])
        qR.append(res[p]["load"][l]["q"][0])
        qS.append(res[p]["load"][l]["q"][1])
        qT.append(res[p]["load"][l]["q"][2])
    loadf = pd.DataFrame({"pR": pR, "pS":pS, "pT": pT, "qR": qR, "qS":qS, "qT": qT})
    potp = loadf["pR"].sum() + loadf["pS"].sum() + loadf["pT"].sum()
    potq = loadf["qR"].sum() + loadf["qS"].sum() + loadf["qT"].sum()
    congestion = np.sqrt(potp**2+potq**2)/(snom.loc[snom["ct"]==int(p[3:])]["snom"].values[0]*1e3)
    R = np.sqrt(loadf["pR"].sum()**2 + loadf["qR"].sum()**2)
    S = np.sqrt(loadf["pS"].sum()**2 + loadf["qS"].sum()**2)
    T = np.sqrt(loadf["pT"].sum()**2 + loadf["qT"].sum()**2)
    imbR = 100*(R/(R+S+T))
    imbS = 100*(S/(R+S+T))
    imbT = 100*(T/(R+S+T))
    plot_residuals(os.path.join(p), res[p]["br"], res[p]["us"], congestion, round(imbR,2), round(imbS,2), round(imbT,2))
exit()
ncondus = []
ncondbr = []
ntrif = []
nmon = []
ncups = []
nodes = []
nodes = []
for r in res:
    ncondbr.append(res[r]["br"]["1"]["condition"])
    ncondus.append(res[r]["us"]["1"]["condition"])
    nodes.append(len(res[r]["voltages"]))
    ntrif.append(res[r]["cups3f"])
    nmon.append(res[r]["cups1f"])
    ncups.append(res[r]["cups1f"]+res[r]["cups3f"])

fig, ax = plt.subplots(figsize=(15,10))
ax.scatter(nodes, ncondbr, edgecolors="k")
ax.scatter(nodes, ncondus, edgecolors="k")
plt.yscale('log')
ax.grid(True)
ax.set_facecolor("gainsboro")
ax.set_xlabel("Number of nodes", fontsize=12, fontname = "Times New Roman")
ax.set_ylabel("Condition number", fontsize=15, fontname="Times New Roman")
fig.savefig(os.path.join("condition.png"), dpi=300)
