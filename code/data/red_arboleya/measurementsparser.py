import pandas as pd
import numpy as np

import os, sys, random
import json
import datetime

ct = "ct-65082"
dateselected = datetime.datetime(2018,5,10,12)

df1 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct1to4.csv"))
df2 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct5to8.csv"))
df3 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct9to12.csv"))
df4 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct13to16.csv"))
df5 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct17to20.csv"))
df6 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct21to24.csv"))
df7 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct25to28.csv"))

columnas = ['Referencia', 'Fecha', 'Dia', 'Estacion', 'Activa E', 'Activa S', 'Reactiva1', 'Reactiva2', 'Reactiva3', 'Reactiva4']

df = pd.concat([df1[columnas],df2[columnas],df3[columnas],df4[columnas],df5[columnas],df6[columnas],df7[columnas]], axis=0)
df.reset_index(drop=True, inplace=True)

meters = []
for i in [df1, df2, df3, df4, df5, df6, df7]:
    meters+=i["Referencia"].drop_duplicates().tolist()

ctcode = []
for i in [df2, df3, df4, df5, df6, df7]:
    ctcode+=i["Codigo Ct"].drop_duplicates().tolist()

ctname = []
for i in [df1, df2, df3, df4, df5, df6, df7]:
    ctname+=i["Nombre Ct"].drop_duplicates().tolist()

loads = pd.read_csv(os.path.join(ct, "loads.csv"))
loads = loads.drop_duplicates(subset=["ID", "PCR"])
loads.reset_index(drop=True, inplace=True)
with open(os.path.join(ct, "net.json"), "r") as f:
    net = json.load(f)   
# Corrección conectividad
newp, r, s, t = [], [], [], []
for _, i in loads.iterrows():
    
    if i["Fase"] not in ["R", "S", "T", "RST"]:
        p = np.random.choice(["R", "S", "T"])
    else:
        p = i["Fase"]
    newp.append(p)
    if p == "R":
        r.append(1.0)
        s.append(0.0)
        t.append(0.0)
    elif p == "S":
        r.append(0.0)
        s.append(1.0)
        t.append(0.0)
    elif p == "T":
        r.append(0.0)
        s.append(0.0)
        t.append(1.0)
    elif p == "RST":
        r.append(0.33)
        s.append(0.33)
        t.append(0.33)

loads["Fase"] = newp
loads["R"] = r
loads["S"] = s
loads["T"] = t
loads["PCR"] = loads["PCR"].astype(str)

#Generación de medidas
df = df.loc[df["Referencia"].isin(loads["ID"].drop_duplicates().tolist())] 
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d/%m/%Y %H:%M")
df = df.loc[df["Fecha"]==dateselected]
df.reset_index(drop=True, inplace=True)

df["p"] = 1000*(df["Activa E"] - df["Activa S"])
df["q"] = 1000*(df["Reactiva1"] + df["Reactiva2"] - df["Reactiva3"] - df["Reactiva4"])

imbalance = {}
for i in net["network"]["bus"]:
    if net["network"]["bus"][i]["load"]:
        pcr = net["network"]["bus"][i]["name"]

        # CUPS que pertenecen al PCR
        cups = loads.loc[loads["PCR"]==pcr]
        if len(cups) == 0:
            continue
            imbalance[pcr] = {}
            imbalance[pcr]["p"] = [0,0,0]
            imbalance[pcr]["q"] = [0,0,0]
        else:
            imbalance[pcr] = {}
            dfc = df.loc[df["Referencia"].isin(cups["ID"].tolist())]
            dfc = dfc[["Referencia", "p", "q"]].merge(cups[["ID", "R", "S", "T"]], left_on="Referencia", right_on="ID", how="inner")
            dfc["pR"] = dfc["p"]*dfc["R"]
            dfc["pS"] = dfc["p"]*dfc["S"]
            dfc["pT"] = dfc["p"]*dfc["T"]
            dfc["qR"] = dfc["q"]*dfc["R"]
            dfc["qS"] = dfc["q"]*dfc["S"]
            dfc["qT"] = dfc["q"]*dfc["T"]
            
            suma = []
            for j in ["pR","pS","pT","qR","qS","qT"]:
                if dfc[j].sum() > 1e6:
                    suma.append(-dfc[j].sum()*1e-3)  #TODO: asumo que hay medidas en origen con las unidades erróneas
                else:
                    suma.append(-dfc[j].sum())

            imbalance[pcr]["p"] = suma[0:3]
            imbalance[pcr]["q"] = suma[3:]

with open(os.path.join(ct,"imbalance.json"), "w") as f:
    json.dump(imbalance,f, indent=4)
