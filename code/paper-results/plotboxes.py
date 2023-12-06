import json
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import os, sys

pathdata = os.path.join("cuerva")

with open(os.path.join(pathdata, "results-us.json"), "r") as f:
    usdata = json.load(f)
with open(os.path.join(pathdata, "results-brazilian.json"), "r") as f:
    brdata = json.load(f)

datoscolumnas = []
for i in range(max(usdata["1"]["n_iterations"],brdata["1"]["n_iterations"])):
    datoscolumnasnew = []
    if str(i+1) in usdata["1"]["residuallist"]:
        datoscolumnasnew.append(usdata["1"]["residuallist"][str(i+1)])
    else:
        datoscolumnasnew.append([])
    if str(i+1) in brdata["1"]["residuallist"]:
        datoscolumnasnew.append(brdata["1"]["residuallist"][str(i+1)])
    else:
        datoscolumnasnew.append([])
    datoscolumnas.append(datoscolumnasnew)

colorus = '#3ACA26'
coloruspoints = '#87E168'
colorbr = '#626461'
colorbrpoints = '#BDBDBD'

boxprops1 = dict(linestyle='-', linewidth=2.0, color=colorus, facecolor=(1,0,0,0.0))
boxprops2 = dict(linestyle='-', linewidth=2.0, color=colorbr, facecolor=(1,0,0,0.0))
medianprops1 = dict(linestyle='-', linewidth=1.5, color='r')
medianprops2 = dict(linestyle='-', linewidth=1.5, color='r')
capprops1 = dict(linestyle='-', linewidth=1.5, color=colorus)
capprops2 = dict(linestyle='-', linewidth=1.5, color=colorbr)
whiskerprops1 = dict(linestyle='-', linewidth=2.0, color=colorus)
whiskerprops2 = dict(linestyle='-', linewidth=2.0, color=colorbr)

fig, ax = plt.subplots(figsize=(15,10))
for i in range(max(usdata["1"]["n_iterations"],brdata["1"]["n_iterations"])):
    
    if len(datoscolumnas[i][0]) == 0:
        #datoscolumnas[i][1] += 1e-15*np.ones(len(datoscolumnas[i][1]))
        datoscolumnas[i][1] = [x for x in datoscolumnas[i][1] if x > 0]
        # Toda la distribución de datos
        data = datoscolumnas[i][1]
        z = i * 2+1
        x = np.random.normal(z, 0.1, len(data))
        ax.plot(x, data, mfc=colorbrpoints, mec=colorbrpoints,
                ms=3, marker="o", linestyle="None")
        #Boxplot
        cajas = ax.boxplot(datoscolumnas[i][1], positions=[i * 2+1], widths=0.6, patch_artist=True,
                           showfliers=False,
                           boxprops=boxprops2,
                           medianprops=medianprops2,
                           capprops=capprops2,
                           whiskerprops=whiskerprops2)
        
        
    elif len(datoscolumnas[i][1]) == 0:
        #datoscolumnas[i][0] += 1e-15*np.ones(len(datoscolumnas[i][0]))
        datoscolumnas[i][0] = [x for x in datoscolumnas[i][0] if x > 0]
        #cajas = ax.boxplot(datoscolumnas[i][0], positions=[i * 2], widths=0.6, patch_artist=True, showfliers=False)
        # Toda la distribución de datos
        data = datoscolumnas[i][0]
        z = i * 2
        x = np.random.normal(z, 0.1, len(data))
        ax.plot(x, data, mfc=coloruspoints, mec=coloruspoints,
                ms=3, marker="o", linestyle="None")
        #Boxplot
        cajas = ax.boxplot(datoscolumnas[i][0], positions=[i * 2], widths=0.6, patch_artist=False,
                           showfliers=False,
                           boxprops=boxprops1,
                           medianprops=medianprops1,
                           capprops=capprops1,
                           whiskerprops=whiskerprops1)
    else:
        #datoscolumnas[i][0] += 1e-15*np.ones(len(datoscolumnas[i][0]))
        #datoscolumnas[i][1] += 1e-15*np.ones(len(datoscolumnas[i][1]))
        datoscolumnas[i][0] = [x for x in datoscolumnas[i][0] if x > 0]
        datoscolumnas[i][1] = [x for x in datoscolumnas[i][1] if x > 0]
        # Toda la distribución de datos
        ## Método US
        data = datoscolumnas[i][0]
        z = i * 2
        x = np.random.normal(z, 0.1, len(data))
        ax.plot(x, data, mfc=coloruspoints, mec=coloruspoints,
                ms=3, marker="o", linestyle="None")
        ## Método BR
        data = datoscolumnas[i][1]
        z = i * 2+1
        x = np.random.normal(z, 0.1, len(data))
        ax.plot(x, data, mfc=colorbrpoints, mec=colorbrpoints,
                ms=3, marker="o", linestyle="None")
        #Boxplot
        cajas = ax.boxplot(datoscolumnas[i][0], positions=[i * 2], widths=0.6, patch_artist=True, 
                           showfliers=False,
                           boxprops=boxprops1,
                           medianprops=medianprops1,
                           capprops=capprops1,
                           whiskerprops=whiskerprops1)
        cajas = ax.boxplot(datoscolumnas[i][1], positions=[i * 2 + 1], widths=0.6, patch_artist=True, 
                           showfliers=False,
                           boxprops=boxprops2,
                           medianprops=medianprops2,
                           capprops=capprops2,
                           whiskerprops=whiskerprops2)
        

    ## Colorear las cajas
    #for caja in cajas['boxes']:
    #    caja.set_facecolor('empty')

# Configurar ejes y etiquetas
ax.set_xticks(np.arange(0.5, max(usdata["1"]["n_iterations"],brdata["1"]["n_iterations"]) * 2, 2))
ax.set_xticklabels([f'Iteration {i+1} \n AUGM_RECT - CURR_INJ' for i in range(max(usdata["1"]["n_iterations"],brdata["1"]["n_iterations"]))], fontname='Times New Roman', fontsize=10)
ax.set_yticklabels(ax.get_yticks(), fontname='Times New Roman', fontsize=10)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.yscale('log')
ax.set_ylim(1e-1*ax.get_yticks()[0], ax.get_yticks()[-1])
ax.set_xlabel('Iterations', fontname='Times New Roman', fontsize=14, fontweight='bold')
ax.set_ylabel('Residual value', fontname='Times New Roman', fontsize=14, fontweight='bold')
ax.grid(True)
ax.set_title('Power residual distribution per iteration and method', fontname='Times New Roman', fontsize=16, fontweight='bold')
fig.savefig(os.path.join(pathdata, "boxplot.pdf"), dpi=300)
# Mostrar el gráfico
plt.show()





