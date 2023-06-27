"""
author: @rcarmona
description: LF simulations
paper: 1

"""

import numpy as np

import json
import random

import os

import pf_lib as pf

import time



def loadJson(path):

    with open(path, 'r') as f:
        jfile = json.load(f)
    
    return jfile

def createImbalancesUS(cases, loads, ps):
    
    imb = {}
    for i in cases:
        imb[i] = {}
        if cases[i]["imbalance"] == None:
            for j in loads:
                imb[i][j] = [round(1/3, 3), round(1/3, 3), round(1/3, 3)]
        elif cases[i]["imbalance"] == "low":
            for j in loads:
                a = random.randrange(30, 40, 5)/100
                b = random.randrange(20, 40, 5)/100
                c = 1 - a - b
                imb_case = [a, b, c]
                imb[i][j] = imb_case
        else:
            for j in loads:
                a = random.randrange(50, 70, 5)/100
                b = random.randrange(0, 30, 5)/100
                c = 1 - a - b
                imb_case = [a, b, c]
                imb[i][j] = imb_case
    
    with open(os.path.join(ps, "imbalance.json"), 'w') as f:
        json.dump(imb, f)
    return imb

def configuration():

    U_ref = [complex(400/np.sqrt(3)*np.cos(0*np.pi/180), 400/np.sqrt(3)*np.sin(0*np.pi/180)),
         complex(400/np.sqrt(3)*np.cos(-120*np.pi/180), 400/np.sqrt(3)*np.sin(-120*np.pi/180)),
         complex(400/np.sqrt(3)*np.cos(120*np.pi/180), 400/np.sqrt(3)*np.sin(120*np.pi/180)),
         0]
    
    V_esp = [231,231,231]
    
    # TODO: estudiar la tolerancia
    tol, n_iter_max = 1e-4, 120
    options = [tol, n_iter_max]

    return U_ref, options, V_esp

def brazilianMethod(cases, net, ref, opts, imb, path_saving, networktype, loads = None):
            
    results = {}
    for t, i in enumerate(cases):
        system_pf = pf.curr_inj()
        if networktype=="cigre":
            system_pf, et = createNetworkUS(system_pf, cases[i], net, ref, loads, imb[i], opts)
        else:
            system_pf, et = createNetworkIngelectus(system_pf, cases[i], net, ref, imb, opts)

        print("Total iteraciones: {}".format(system_pf.iter_spent))

        results[i] = {}
        results[i]["type"] = cases[i]
        results[i]["n_iterations"] = system_pf.iter_spent
        results[i]["condition"] = np.linalg.cond(system_pf.J)
        results[i]["residuals"] = system_pf.lista_residuos
        results[i]["elapsed_time"] = et
        results[i]["tol"] = opts[0]
        if system_pf.iter_spent == 120:
            results[i]["converge"] = False
        else:
            results[i]["converge"] = True
        #if t == 2: break

        
        results[i]["voltages"] = system_pf.voltages_iter
        results[i]["currents"] = system_pf.current_iter

    with open(os.path.join(path_saving, "results-brazilian.json"), 'w') as f:
        json.dump(results, f)
    
    #check1KL(system_pf)

def USMethod(cases, net, ref, opts, imb, path_saving, networktype, loads = None):
        
    results = {}
    for t, i in enumerate(cases):
        system_pf = pf.aug_rect()
        if networktype=="cigre":
            system_pf, et = createNetworkUS(system_pf, cases[i], net, ref, loads, imb[i], opts)
        else:
            system_pf, et = createNetworkIngelectus(system_pf, cases[i], net, ref, imb, opts)

        print("Total iteraciones: {}".format(system_pf.iter_spent))
        
        results[i] = {}
        results[i]["type"] = cases[i]
        results[i]["n_iterations"] = system_pf.iter_spent
        results[i]["condition"] = np.linalg.cond(system_pf.J)
        results[i]["residuals"] = system_pf.lista_residuos
        results[i]["elapsed_time"] = et
        results[i]["tol"] = opts[0]
        if system_pf.iter_spent == 120:
            results[i]["converge"] = False
        else:
            results[i]["converge"] = True
        results[i]["voltages"] = system_pf.voltages_iter
        results[i]["currents"] = system_pf.current_iter
        #if t == 2: break
    with open(os.path.join(path_saving, "results-us.json"), 'w') as f:
        json.dump(results, f)
    
    #check1KL(system_pf)

def createNetworkUS(system_pf, c, net, ref, loads, imb, opts):
    for i in net["network"]["bus"]:
        ln = net["network"]["bus"][i]["name"] # Load name
        if net["network"]["bus"][i]["slack"]:
            system_pf.add_bus(int(i), P = None, Q = None, U = ref, Zg = 0.01, name = 'Slack')   # TODO: ¿por qué Zg = 0.01?
        else:
            if net["network"]["bus"][i]["load"]:
                lb = loads[ln]["s"]*1e3 #Multiplicamos por 1e3 en el caso de la red de la CIGRE
                pf = loads[ln]["pf"]
                if c["name"] == "consumption":
                    sign = -1
                elif c["name"] == "generation":
                    sign = 1
                else:
                    if loads[ln]["pv"]:
                        sign = 1
                    else:
                        sign = -1
                system_pf.add_bus(int(i), P = list(sign*lb*pf*np.array(imb[ln])), Q = list(sign*lb*np.sin(np.arccos(pf))*np.array(imb[ln])), U = None, Zg = c["r_earthing"])
            else:
                system_pf.add_bus(int(i), P = [0,0,0], Q = [0,0,0], U = None, Zg = None)
    
    for j in net["network"]["branch"]:
        tp = net["network"]["branch"][j]["type"]  # Line type
        length = net["network"]["branch"][j]["length"]    # Line length
        nin = net["network"]["branch"][j]["nodefrom"]
        nout = net["network"]["branch"][j]["nodeto"]
        system_pf.add_line(tp, length,  nin,  nout)
    
    
    tini = time.time() # Time initial
    
    system_pf.solve(opts)

    elapsedtime = time.time() - tini

    return system_pf, elapsedtime

def createNetworkIngelectus(system_pf, c, net, ref, imb, opts):
    for i in net["network"]["bus"]:
        ln = net["network"]["bus"][i]["name"] # Load name
        if net["network"]["bus"][i]["slack"]:
            system_pf.add_bus(int(i), P = None, Q = None, U = ref, Zg = 0.01, name = 'Slack')
        else:
            if net["network"]["bus"][i]["load"]:
                p = imb[ln]["p"]
                q = imb[ln]["q"]
                system_pf.add_bus(int(i), P = [p[0], p[1], p[2]], Q = [q[0], q[1], q[2]], U = None, Zg = c["r_earthing"])
            else:
                system_pf.add_bus(int(i), P = [0,0,0], Q = [0,0,0], U = None, Zg = None)
    
    for j in net["network"]["branch"]:
        tp = net["network"]["branch"][j]["type"]  # Line type
        length = net["network"]["branch"][j]["length"]    # Line length
        nin = net["network"]["branch"][j]["nodefrom"]
        nout = net["network"]["branch"][j]["nodeto"]
        system_pf.add_line(tp, length,  nin,  nout)
    
    
    tini = time.time() # Time initial
    
    system_pf.solve(opts)

    elapsedtime = time.time() - tini

    return system_pf, elapsedtime

def check1KL(system_pf):
    print("Comprobaciones")
    print('1KL:')
    for bus in system_pf.buses[1:]:
        I = np.copy(bus.I)
        if bus.Zg != None:
            I[3] -= bus.U[3]/bus.Zg
        for line in bus.connections:
            if line.connections[0] == bus:
                I -= line.I
            else:
                I += line.I
        print(f'\t Bus {bus.ref}: {np.abs(I)}')

def main():

    # File saving
    name = "test18-redcigre-initB-1e-4"
    path_saving = os.path.join("results", name)
    if not os.path.exists(path_saving): os.makedirs(path_saving)

    # Configuration
    ref, opts, v_esp = configuration()
    networktype = "cigre" # Options "cigre", "red_cuerva", "red_arboleya"

    if networktype == "cigre":
        # Data path
        path_cases = os.path.join("data", networktype, "cases.json")
        path_net = os.path.join("data", networktype, "net.json")
        path_loads = os.path.join("data", networktype, "loads.json")
        # Load data
        cases = loadJson(path_cases)
        net = loadJson(path_net)
        loads = loadJson(path_loads)

        # Create imbalances scenarios
        imbalances = createImbalancesUS(cases, loads, path_saving)
        with open(os.path.join(path_saving, "scenario-cigre.json"), 'w') as f:
            json.dump(imbalances, f)

        # Execute brazilian method
        brazilianMethod(cases, net, ref, opts, imbalances, path_saving, networktype, loads)
        # Execute US method
        USMethod(cases, net, ref, opts, imbalances, path_saving, networktype, loads)
    elif networktype == "red_cuerva":
        # Data path
        path_cases = os.path.join("data", networktype, "cases.json")
        path_net = os.path.join("data", networktype, "net.json")
        path_imb = os.path.join("data", networktype, "imbalance.json")
        # Load data
        cases = loadJson(path_cases)
        net = loadJson(path_net)
        # Create imbalances scenarios
        imbalances = loadJson(path_imb)

        # Execute brazilian method
        brazilianMethod(cases, net, ref, opts, imbalances, path_saving, networktype)
        
        # Execute US method
        USMethod(cases, net, ref, opts, imbalances, path_saving, networktype)

if __name__ == "__main__":
    main()

