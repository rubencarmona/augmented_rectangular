import pandas as pd
import json
import numpy as np

import matplotlib.pyplot as plt
import sys, os


def plot_residuals(braz, us, cong, a, b, c):

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
    fig.savefig(os.path.join("residuals.png"), dpi=300)
    ax.plot(kind="line")


res = {}
snom = 630
res["cuerva"] = {}

with open("results-us.json", "r") as f:
    res["cuerva"]["us"] = json.load(f)
with open("results-brazilian.json", "r") as f:
    res["cuerva"]["br"] = json.load(f)
res["cuerva"]["voltages"] = pd.read_csv("voltages.csv")

with open("imbalance.json", "r") as f:
    res["cuerva"]["load"] = json.load(f)
pR, pS, pT, qR, qS, qT = [], [], [], [], [], []
for l in res["cuerva"]["load"]:
    pR.append(res["cuerva"]["load"][l]["p"][0])
    pS.append(res["cuerva"]["load"][l]["p"][1])
    pT.append(res["cuerva"]["load"][l]["p"][2])
    qR.append(res["cuerva"]["load"][l]["q"][0])
    qS.append(res["cuerva"]["load"][l]["q"][1])
    qT.append(res["cuerva"]["load"][l]["q"][2])
loadf = pd.DataFrame({"pR": pR, "pS":pS, "pT": pT, "qR": qR, "qS":qS, "qT": qT})
potp = loadf["pR"].sum() + loadf["pS"].sum() + loadf["pT"].sum()
potq = loadf["qR"].sum() + loadf["qS"].sum() + loadf["qT"].sum()

R = np.sqrt(loadf["pR"].sum()**2 + loadf["qR"].sum()**2)
S = np.sqrt(loadf["pS"].sum()**2 + loadf["qS"].sum()**2)
T = np.sqrt(loadf["pT"].sum()**2 + loadf["qT"].sum()**2)
congestion = np.sqrt(potp**2+potq**2)/(630*1e3)
imbR = 100*(R/(R+S+T))
imbS = 100*(S/(R+S+T))
imbT = 100*(T/(R+S+T))

plot_residuals(res["cuerva"]["br"], res["cuerva"]["us"], congestion, round(imbR,2), round(imbS,2), round(imbT,2))

number = len(res.keys())
