import pandas as pd
import numpy as np

from math import e

import os
import sys

import json


df = pd.read_csv(os.path.join("cableimpedances.csv"))
with open(os.path.join("parametering.json"), "r") as f:
    param = json.load(f)
originalarboleya = False

# Other parameters
rearth =(np.pi**2)*50*1e-4
k1 = 2e-4
k2 = 658.38

if originalarboleya:
    c = {}
    for _, r in df.iterrows():
        c[r["code"]] = {}
        c[r["code"]]["real"] = [[r["r_phase"], 0.0, 0.0, 0.0],
                                [0.0, r["r_phase"], 0.0, 0.0],
                                [0.0, 0.0, r["r_phase"], 0.0],
                                [0.0, 0.0, 0.0, r["r_neutral"]]]
        c[r["code"]]["image"] = [[r["x_phase"], 0.0, 0.0, 0.0],
                                [0.0, r["x_phase"], 0.0, 0.0],
                                [0.0, 0.0, r["x_phase"], 0.0],
                                [0.0, 0.0, 0.0, r["x_neutral"]]]
    with open(os.path.join("cableparametersarboleya.json"), "w") as f:
        json.dump(c, f)
else:
    c = {}
    for _, r in df.iterrows():
        c[r["code"]] = {}
        if r["kind"] == "Aéreo":
            # Za, Zb, Zc
            rf = param["aereo"][str(int(r["sectionphase"]))]["R20"]*(1+0.00392*(40-20))   # Cálculo para fase a 40º
            rn = param["aereo"][str(int(r["sectionneutral"]))]["R20"]*(1+0.00392*(30-20))   # Cálculo para fase a 30º
            rphase = rf + rearth    # En Ohm/km
            xphase = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(0.75*param["aereo"][str(int(r["sectionphase"]))]["D"]/2))
            rneutral = rn + rearth    # En Ohm/km
            xneutral = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(0.75*param["aereo"][str(int(r["sectionneutral"]))]["D"]/2))
            
            # Zab, Zbc, Zcn
            rab = rearth
            rbc = rearth
            rcn = rearth
            xab = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300))  
            xbc = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300))  
            xcn  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300))  
            # Zac, Zbn
            rac = rearth
            rbn = rearth
            xac = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300)) 
            xbn  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300))  
            # Zan
            ran = rearth
            xan  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(300))  


            rff = (1/3)*(rab+rbc+rac)
            xff = (1/3)*(xab+xbc+xac)
            rfn = (1/3)*(ran+rbn+rcn)
            xfn = (1/3)*(xan+xbn+xcn)

            c[r["code"]]["real"] = [[rphase, rff, rff, rfn],
                                    [rff, rphase, rff, rfn],
                                    [rff, rff, rphase, rfn],
                                    [rff, rff, rff, rneutral]]
            c[r["code"]]["image"] = [[xphase, xff, xff, xfn],
                                    [xff, xphase, xff, xfn],
                                    [xff, xff, xphase, xfn],
                                    [xff, xff, xff, xneutral]]
        else:
            if r["material"] == "Al":
                rf = param["subterraneoAl"][str(int(r["sectionphase"]))]["R20"]*(1+0.00403*(40-20))   # Cálculo para fase a 40º
                rn = param["subterraneoAl"][str(int(r["sectionneutral"]))]["R20"]*(1+0.00403*(30-20))   # Cálculo para fase a 30º

                Dcp = param["subterraneoAl"][str(int(r["sectionphase"]))]["Dcable"]
                Dcn = param["subterraneoAl"][str(int(r["sectionneutral"]))]["Dcable"]
                
                Dp = param["subterraneoAl"][str(int(r["sectionphase"]))]["Dconductor"]
                Dn = param["subterraneoAl"][str(int(r["sectionneutral"]))]["Dconductor"]

            else:
                rf = param["subterraneoCu"][str(int(r["sectionphase"]))]["R20"]*(1+0.00403*(40-20))   # Cálculo para fase a 40º
                rn = param["subterraneoCu"][str(int(r["sectionneutral"]))]["R20"]*(1+0.00403*(30-20))   # Cálculo para fase a 30º

                Dcp = param["subterraneoCu"][str(int(r["sectionphase"]))]["Dcable"]
                Dcn = param["subterraneoCu"][str(int(r["sectionneutral"]))]["Dcable"]
                
                Dp = param["subterraneoCu"][str(int(r["sectionphase"]))]["Dconductor"]
                Dn = param["subterraneoCu"][str(int(r["sectionneutral"]))]["Dconductor"]
        
            # Distancias fase-fase y fase-neutro
            dab = dbc = Dcp
            dac = np.sqrt(2)*dab

            dan = dcn = (Dcp+Dcn)/2
            dbn = np.sqrt(2)*Dcp

            # Impedancias
            rphase = rf + rearth    # En Ohm/km
            xphase = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/((e**(-1/4))*(Dp/2)))
            rneutral = rn + rearth    # En Ohm/km
            xneutral = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/((e**(-1/4))*(Dn/2)))
            
            # Zab, Zbc, Zcn
            rab = rearth
            rbc = rearth
            rcn = rearth
            xab = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dab))  
            xbc = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dbc))  
            xcn  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dcn))  
            # Zac, Zbn
            rac = rearth
            rbn = rearth
            xac = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dac)) 
            xbn  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dbn))  
            # Zan
            ran = rearth
            xan  = (2*np.pi*50)*k1*np.log((k2*np.sqrt((200/50)))/(dan))  

            rff = (1/3)*(rab+rbc+rac)
            xff = (1/3)*(xab+xbc+xac)
            rfn = (1/3)*(ran+rbn+rcn)
            xfn = (1/3)*(xan+xbn+xcn)

            c[r["code"]]["real"] = [[rphase, rff, rff, rfn],
                                    [rff, rphase, rff, rfn],
                                    [rff, rff, rphase, rfn],
                                    [rff, rff, rff, rneutral]]
            c[r["code"]]["image"] = [[xphase, xff, xff, xfn],
                                    [xff, xphase, xff, xfn],
                                    [xff, xff, xphase, xfn],
                                    [xff, xff, xff, xneutral]]


    with open(os.path.join("cableparametersarboleyafull.json"), "w") as f:
        json.dump(c, f, indent=4)
