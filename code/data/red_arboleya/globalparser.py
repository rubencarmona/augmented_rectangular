import pandas as pd
import numpy as np

import json
import sys, os

import datetime

# Loading measurements just one time
# Measurements
df1 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct1to4.csv"))
df2 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct5to8.csv"))
df3 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct9to12.csv"))
df4 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct13to16.csv"))
df5 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct17to20.csv"))
df6 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct21to24.csv"))
df7 = pd.read_csv(os.path.join("data_original", "metermeasurement", "energymeas-meters-ct25to28.csv"))
columnas = ['Referencia', 'Fecha', 'Dia', 'Estacion', 'Activa E', 'Activa S', 'Reactiva1', 'Reactiva2', 'Reactiva3', 'Reactiva4']
#ct = "ct-65082"
for ct in os.listdir():
    if "ct-1136056" not in ct: continue
    print("Vamos por el CT: {}".format(ct.split("-")[1]))
    df = pd.concat([df1[columnas],df2[columnas],df3[columnas],df4[columnas],df5[columnas],df6[columnas],df7[columnas]], axis=0)
    df.reset_index(drop=True, inplace=True)

    dateselected = datetime.datetime(2018,5,10,12)

    # Topology
    try:
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
            net["network"]["branch"][j]["length"] = i["length"]#*1e-3 #TODO: NO ESTOY SEGURO DE ASIGNARLE SU LONGITUD O ON PORQUE NO SÉ SI ES UNITARIO

        with open(os.path.join(ct,"net.json"), "w") as f:
            json.dump(net,f, indent=4)

        # Measurements
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

        #meters = []
        #for i in [df1, df2, df3, df4, df5, df6, df7]:
        #    meters+=i["Referencia"].drop_duplicates().tolist()
    #
        #ctcode = []
        #for i in [df2, df3, df4, df5, df6, df7]:
        #    ctcode+=i["Codigo Ct"].drop_duplicates().tolist()
    #
        #ctname = []
        #for i in [df1, df2, df3, df4, df5, df6, df7]:
        #    ctname+=i["Nombre Ct"].drop_duplicates().tolist()

        loads = pd.read_csv(os.path.join(ct, "loads.csv"))
        loads = loads.drop_duplicates(subset=["ID", "PCR"])
        loads.reset_index(drop=True, inplace=True)
        # Corrección conectividad
        #np.seed(20)
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
                pr = np.random.uniform(0.4,1)
                ps = np.random.uniform(0,pr) 
                pt = (1-pr-ps)
                r.append(pt)
                s.append(pr)
                t.append(ps)

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
        #TODO: primer chequeo de valores elevados
        for _, dfr in df.iterrows():
            if dfr["Activa E"] > 1e3:
                df.loc[_,"Activa E"] = dfr["Activa E"]*1e-3
            if dfr["Activa S"] > 1e3:
                df.loc[_,"Activa S"] = dfr["Activa S"]*1e-3
            if dfr["Reactiva1"] > 1e3:
                df.loc[_,"Reactiva1"] = dfr["Reactiva1"]*1e-3
            if dfr["Reactiva2"] > 1e3:
                df.loc[_,"Reactiva2"] = dfr["Reactiva2"]*1e-3
            if dfr["Reactiva3"] > 1e3:
                df.loc[_,"Reactiva3"] = dfr["Reactiva3"]*1e-3
            if dfr["Reactiva4"] > 1e3:
                df.loc[_,"Reactiva4"] = dfr["Reactiva4"]*1e-3

        df["p"] = 1000*(df["Activa E"] - df["Activa S"])*15#*6*np.random.uniform(0,1)
        df["q"] = 1000*(df["Reactiva1"] + df["Reactiva2"] - df["Reactiva3"] - df["Reactiva4"])*15#*6*np.random.uniform(0,1)

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
                        if dfc[j].sum() > 1e5:
                            suma.append(-dfc[j].sum()*1e-3)  #TODO: asumo que hay medidas en origen con las unidades erróneas
                        else:
                            suma.append(-dfc[j].sum())

                    imbalance[pcr]["p"] = suma[0:3]
                    imbalance[pcr]["q"] = suma[3:]

        with open(os.path.join(ct,"imbalance.json"), "w") as f:
            json.dump(imbalance,f, indent=4)
    except Exception as e:
        print("Ha ocurrido el siguiente error: {}".format(e))
        continue

