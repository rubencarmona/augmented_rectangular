import pandas as pd
import numpy as np

import json

import os

import matplotlib.pyplot as plt

def loadJson(path):

    with open(path, 'r') as f:
        jfile = json.load(f)
    
    return jfile
def voltage_evolution():
    return None

def plot_residuals(path_res, braz, us, type = ["consumption", "generation", "both"], converge=True):

    # Plot brazilian
    fig, ax = plt.subplots(figsize=(15,10))
    greater = 0
    tolerance = 0.0
    for i in braz:
        tolerance = braz[i]["tol"]
        if ((braz[i]["converge"]==converge) and (braz[i]["type"]["name"] in type)):
            if len(braz[i]["residuals"]) > greater: greater = len(braz[i]["residuals"])
            x = np.linspace(1,len(braz[i]["residuals"]),len(braz[i]["residuals"])).astype(int)
            y = braz[i]["residuals"]
            ax.plot(x, y, ls='-.', linewidth = 2.5, marker = 'o', color='grey')
    for i in us:
        if ((us[i]["converge"]==converge) and (us[i]["type"]["name"] in type)):
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
    
    if type == ["consumption", "generation", "both"]:
        tp = "all"
    else:
        tp = type[0]
    ax.set_title("Evolution of residual per iteration. Tolerance rate: {}. Cases type: {}".format(tolerance, tp),fontsize=20, fontname="Times New Roman")
    #plt.show()
    fig.savefig(os.path.join(path_res, "residuals-{}.png".format(tp)), dpi=300)
    ax.plot(kind="line")

def plot_convergence(braz, us, ps, type = ["consumption", "generation", "both"], imbalance = [None, "high", "low"]):

    cvgNoneBraz, ncvgNoneBraz, cvg2Braz, ncvg2Braz, cvg40Braz, ncvg40Braz = 0, 0, 0, 0, 0, 0
    cvgNoneUS, ncvgNoneUS, cvg2US, ncvg2US, cvg40US, ncvg40US = 0, 0, 0, 0, 0, 0
    for i in braz:
        if ((braz[i]["type"]["imbalance"] in imbalance) and (braz[i]["type"]["name"] in type)):
            if braz[i]["type"]["r_earthing"] == None:
                if braz[i]["converge"]:
                    cvgNoneBraz += 1
                else:
                    ncvgNoneBraz += 1
            elif braz[i]["type"]["r_earthing"] == 2:
                if braz[i]["converge"]:
                    cvg2Braz += 1
                else:
                    ncvg2Braz += 1
            elif braz[i]["type"]["r_earthing"] == 40:
                if braz[i]["converge"]:
                    cvg40Braz += 1
                else:
                    ncvg40Braz += 1
    for i in us:
        if ((us[i]["type"]["imbalance"] in imbalance) and (us[i]["type"]["name"] in type)):
            if us[i]["type"]["r_earthing"] == None:
                if us[i]["converge"]:
                    cvgNoneUS += 1
                else:
                    ncvgNoneUS += 1
            elif us[i]["type"]["r_earthing"] == 2:
                if us[i]["converge"]:
                    cvg2US += 1
                else:
                    ncvg2US += 1
            elif us[i]["type"]["r_earthing"] == 40:
                if us[i]["converge"]:
                    cvg40US += 1
                else:
                    ncvg40US += 1
    
    # Rates

    rcvgNoneBraz = 100*(cvgNoneBraz)/(cvgNoneBraz+ncvgNoneBraz)
    rncvgNoneBraz = 100*(ncvgNoneBraz)/(cvgNoneBraz+ncvgNoneBraz)
    rcvg2Braz = 100*(cvg2Braz)/(cvg2Braz+ncvg2Braz)
    rncvg2Braz = 100*(ncvg2Braz)/(cvg2Braz+ncvg2Braz)
    rcvg40Braz = 100*(cvg40Braz)/(cvg40Braz+ncvg40Braz)
    rncvg40Braz = 100*(ncvg40Braz)/(cvg40Braz+ncvg40Braz)
    rcvgNoneUS = 100*(cvgNoneUS)/(cvgNoneUS+ncvgNoneUS)
    rncvgNoneUS = 100*(ncvgNoneUS)/(cvgNoneUS+ncvgNoneUS)
    rcvg2US = 100*(cvg2US)/(cvg2US+ncvg2US)
    rncvg2US = 100*(ncvg2US)/(cvg2US+ncvg2US)
    rcvg40US = 100*(cvg40US)/(cvg40US+ncvg40US)
    rncvg40US = 100*(ncvg40US)/(cvg40US+ncvg40US)

    rates = {
        "rcvgNoneBraz": rcvgNoneBraz,
        "rncvgNoneBraz": rncvgNoneBraz,
        "rcvg2Braz": rcvg2Braz,
        "rncvg2Braz": rncvg2Braz,
        "rcvg40Braz": rcvg40Braz,
        "rncvg40Braz": rncvg40Braz,
        "rcvgNoneUS": rcvgNoneUS,
        "rncvgNoneUS": rncvgNoneUS,
        "rcvg2US": rcvg2US,
        "rncvg2US": rncvg2US,
        "rcvg40US": rcvg40US,
        "rncvg40US": rncvg40US
    }

    with open(os.path.join(ps, "conv-rates.json"), 'w') as f:
        json.dump(rates, f)
    

def plot_conditionnumber(path_res,ncases, braz, us, tp):

    condus = []
    condbraz = []
    cases = []

    for i in range(1,ncases+1):
        cases.append("Case {}".format(i))
        condbraz.append(braz[str(i)]["condition"])
        condus.append(us[str(i)]["condition"])

    data = pd.DataFrame({"case": cases, "Condition Number Brazilian": condbraz, "Condition Number US":condus})
    
    fig, ax = plt.subplots(figsize=(15,10))
    data.plot(y=['Condition Number Brazilian', 'Condition Number US'], ax=ax, color=['grey', 'red'], width = 0.5, kind='bar', stacked=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_facecolor("gainsboro")
    vals = ax.get_yticks()
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)
    ax.set_xlabel("Cases", fontname='Serif', fontsize=14)
    ax.set_ylabel("Cond(J)", fontname='Serif', fontsize=14)
    ax.set_xticks(np.arange(len(data['case'])))
    ax.set_xticklabels(data['case'].tolist(),fontname='Serif', fontsize=12, rotation=90)
    ax.set_yticklabels(ax.get_yticks(minor=False),fontname='Serif', fontsize=12)
    ax.legend(loc='upper right', prop={'family':'Serif', 'size':12})
    plt.yscale('log')
    ax.set_title("Condition number comparison. Cases type: {}".format(tp),fontsize=20, fontname="Times New Roman")
    
    #plt.show()
    fig.savefig(os.path.join(path_res, "conditionnumber-{}.png".format(tp)), dpi=300)

def plotLineVoltage(df, pathsaving):

    #fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(10, 4))
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(20, 10))
    d = {
        "R": {"g": ax1, "cl": "tomato", "c": "red"},
        "S": {"g": ax2, "cl": "tomato", "c": "red"}, 
        "T": {"g": ax3, "cl": "tomato", "c": "red"},
        "N": {"g": ax4, "cl": "tomato", "c": "red"}
    }

    limits = {"min": min(df["vR_us"].min(),df["vS_us"].min(), df["vT_us"].min()),
              "max": max(df["vR_us"].max(),df["vS_us"].max(), df["vT_us"].max())}
    for i in d:
        d[i]["g"].plot(df["node"].tolist(), df["v{}_us".format(i)], linewidth=2, color=d[i]["cl"], label="Phase {}".format(i))
        d[i]["g"].plot(df["node"].tolist(), df["v{}_us".format(i)], "o", color=d[i]["c"])
        d[i]["g"].legend(loc="best")
        d[i]["g"].set_ylabel("Voltage (V)",fontsize=14, fontname="Times New Roman")
        if ((i == "T") | (i == "N")): d[i]["g"].set_xlabel("Nodes",fontsize=14, fontname="Times New Roman")
        d[i]["g"].set_title("Voltage evolution through the grid in phase {}".format(i),fontsize=18, fontname="Times New Roman")
        d[i]["g"].grid()
        if i == "N": continue
        d[i]["g"].set_ylim(limits["min"]-2, limits["max"]+2)
    fig.savefig(os.path.join(pathsaving, "voltageevolution.pdf"), dpi=300)

def plotLineCurrents(df, pathsaving):

    #fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(10, 4))
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=(20, 10))
    d = {
        "R": {"g": ax1, "cl": "tomato", "c": "red"},
        "S": {"g": ax2, "cl": "tomato", "c": "red"}, 
        "T": {"g": ax3, "cl": "tomato", "c": "red"},
        "N": {"g": ax4, "cl": "tomato", "c": "red"}
    }

    limits = {"min": min(df["iR_us"].min(),df["iS_us"].min(), df["iT_us"].min()),
              "max": max(df["iR_us"].max(),df["iS_us"].max(), df["iT_us"].max())}
    for i in d:
        d[i]["g"].plot(df["line"].tolist(), df["i{}_us".format(i)], linewidth=2, color=d[i]["cl"], label="Phase {}".format(i))
        d[i]["g"].plot(df["line"].tolist(), df["i{}_us".format(i)], "o", color=d[i]["c"])
        d[i]["g"].legend(loc="best")
        d[i]["g"].set_ylabel("Current (A)",fontsize=14, fontname="Times New Roman")
        if ((i == "T") | (i == "N")): d[i]["g"].set_xlabel("Lines",fontsize=14, fontname="Times New Roman")
        d[i]["g"].set_title("Current evolution through the grid in phase {}".format(i),fontsize=18, fontname="Times New Roman")
        d[i]["g"].grid()
        if i == "N": continue
        d[i]["g"].set_ylim(limits["min"]-2, limits["max"]+2)
    fig.savefig(os.path.join(pathsaving, "currentevolution.pdf"), dpi=300)

def plot_times(path_res, ncases, braz, us, tp):

    condus = []
    condbraz = []
    cases = []

    for i in range(1,ncases+1):
        cases.append("Case {}".format(i))
        condbraz.append(braz[str(i)]["elapsed_time"])
        condus.append(us[str(i)]["elapsed_time"])

    data = pd.DataFrame({"case": cases, "Timing Brazilian": condbraz, "Timing US":condus})
    
    fig, ax = plt.subplots(figsize=(15,10))
    data.plot(y=['Timing Brazilian', 'Timing US'], ax=ax, color=['grey', 'red'], width = 0.5, kind='bar', stacked=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_facecolor("gainsboro")
    vals = ax.get_yticks()
    for tick in vals:
        ax.axhline(y=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)
    ax.set_xlabel("Cases", fontname='Serif', fontsize=14)
    ax.set_ylabel("Elapsed time to convergence (s)", fontname='Serif', fontsize=14)
    ax.set_xticks(np.arange(len(data['case'])))
    ax.set_xticklabels(data['case'].tolist(),fontname='Serif', fontsize=12, rotation=90)
    ax.set_yticklabels(ax.get_yticks(minor=False),fontname='Serif', fontsize=12)
    ax.legend(loc='upper right', prop={'family':'Serif', 'size':12})
    ax.set_title("Convergence timing comparison. Cases type: {}".format(tp),fontsize=20, fontname="Times New Roman")

    #plt.show()
    fig.savefig(os.path.join(path_res, "timing-{}.png".format(tp)), dpi=300)

def main():

    # Data import
    name = "test11-redcigre-initA-1e-7"
    networktype = "cigre" # Options "cigre", "red_cuerva", "red_arboleya"
    path_res = os.path.join("results", name)
    path_cases = os.path.join("data", networktype, "cases.json")
    path_net = os.path.join("data", networktype, "net.json")
    #path_loads = os.path.join("data", networktype, "loads.json")

    cases = loadJson(path_cases)
    net = loadJson(path_net)
    #loads = loadJson(path_loads)
    results_bra = loadJson(os.path.join(path_res, "results-brazilian.json"))
    results_us = loadJson(os.path.join(path_res, "results-us.json"))

    #poss = ["consumption"]
    #poss = ["generation"]
    #poss = ["both"]
    poss = ["consumption", "generation", "both"]
    if poss == ["consumption", "generation", "both"] :
        pss = "all"
    else:
        pss = poss[0]
    plot_residuals(path_res,results_bra, results_us, poss)
    plot_convergence(results_bra, results_us, path_res, poss)
    plot_conditionnumber(path_res,len(cases), results_bra, results_us, pss)
    plot_times(path_res,len(cases), results_bra, results_us, pss)

    return None


if __name__ == "__main__":
    main()