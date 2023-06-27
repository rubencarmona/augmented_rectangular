import numpy as np
import json

import os
import sys

#line_type = {'OH1': np.array([[0.540 + 0.777j, 0.049 + 0.505j, 0.049 + 0.462j, 0.049 + 0.436j],
#                              [0.049 + 0.505j, 0.540 + 0.777j, 0.049 + 0.505j, 0.049 + 0.462j],
#                              [0.049 + 0.462j, 0.049 + 0.505j, 0.540 + 0.777j, 0.049 + 0.505j],
#                              [0.049 + 0.436j, 0.049 + 0.462j, 0.049 + 0.505j, 0.540 + 0.777j]]),       
#             'OH2': np.array([[1.369 + 0.812j, 0.049 + 0.505j, 0.049 + 0.462j, 0.049 + 0.436j],
#                              [0.049 + 0.505j, 1.369 + 0.812j, 0.049 + 0.505j, 0.049 + 0.462j],
#                              [0.049 + 0.462j, 0.049 + 0.505j, 1.369 + 0.812j, 0.049 + 0.505j],
#                              [0.049 + 0.436j, 0.049 + 0.462j, 0.049 + 0.505j, 1.369 + 0.812j]]),
#             'OH3': np.array([[2.065 + 0.825j, 0.049 + 0.505j, 0.049 + 0.462j, 0.049 + 0.436j],
#                              [0.049 + 0.505j, 2.065 + 0.825j, 0.049 + 0.505j, 0.049 + 0.462j],
#                              [0.049 + 0.462j, 0.049 + 0.505j, 2.065 + 0.825j, 0.049 + 0.505j],
#                              [0.049 + 0.436j, 0.049 + 0.462j, 0.049 + 0.505j, 2.065 + 0.825j]]),
#             'UG1': np.array([[0.211 + 0.747j, 0.049 + 0.673j, 0.049 + 0.651j, 0.049 + 0.673j], 
#                              [0.049 + 0.673j, 0.211 + 0.747j, 0.049 + 0.673j, 0.049 + 0.651j],
#                              [0.049 + 0.651j, 0.049 + 0.673j, 0.211 + 0.747j, 0.049 + 0.673j],
#                              [0.049 + 0.673j, 0.049 + 0.651j, 0.049 + 0.673j, 0.211 + 0.747j]]),
#             'UG2': np.array([[0.314 + 0.762j, 0.049 + 0.687j, 0.049 + 0.665j, 0.049 + 0.687j], 
#                              [0.049 + 0.687j, 0.314 + 0.762j, 0.049 + 0.687j, 0.049 + 0.665j],
#                              [0.049 + 0.665j, 0.049 + 0.687j, 0.314 + 0.762j, 0.049 + 0.687j],
#                              [0.049 + 0.687j, 0.049 + 0.665j, 0.049 + 0.687j, 0.314 + 0.762j]]),
#             'UG3': np.array([[0.871 + 0.797j, 0.049 + 0.719j, 0.049 + 0.697j, 0.049 + 0.719j],
#                              [0.049 + 0.719j, 0.871 + 0.797j, 0.049 + 0.719j, 0.049 + 0.697j],
#                              [0.049 + 0.697j, 0.049 + 0.719j, 0.871 + 0.797j, 0.049 + 0.719j],
#                              [0.049 + 0.719j, 0.049 + 0.697j, 0.049 + 0.719j, 0.871 + 0.797j]])}     

with open(os.path.join("data", "cables", "cableparameters.json"), 'r') as f:
    lt = json.load(f)

line_type = {}
for i in lt:
    param = []
    rl = lt[i]["real"]
    img = lt[i]["image"]
    for j in range(4):
        param.append([rl[j][0]+img[j][0]*1j,
                      rl[j][1]+img[j][1]*1j,
                      rl[j][2]+img[j][2]*1j,
                      rl[j][3]+img[j][3]*1j])
    line_type[i] = np.array(param)

class grid(object):
    def __init__(self):
        self.buses = list()
        self.lines = list()
        
    def add_bus(self, ref, P, Q, U, Zg = None, V_esp = False, name = None):
        if ref == 0:
            tipo = 'Slack'
        else:
            if V_esp is not False:
                tipo = 'PV'
            else:
                tipo = 'PQ'                                       
        self.buses.append(bus(ref, P, Q, U, Zg, tipo, V_esp, name))  
            
    def add_line(self, Z, long, bus_0, bus_1):
        for bus in self.buses:
            if bus.ref == bus_0:
                BUS_0 = bus
            if bus.ref == bus_1:
                BUS_1 = bus
        self.lines.append(line(Z, long, BUS_0, BUS_1))
        BUS_0.connections.append(self.lines[-1])
        BUS_1.connections.append(self.lines[-1])

class line:
    def __init__(self, Z, long, BUS_0, BUS_1):
        if isinstance(Z, str):
            self.Z = line_type[Z]*long/1000
        else:
            self.Z = Z
        self.long = long
        self.I = None
        self.connections = [BUS_0, BUS_1]
        
class bus:
    def __init__(self, ref, P, Q, U, Zg, tipo, V_esp, name):
        self.ref = ref
        self.P = P
        self.Q = Q
        self.U = U
        self.Zg = Zg
        self.type = tipo
        self.I = [0, 0, 0, 0]
        self.V_esp = V_esp
        self.name = name
        self.connections = list()
    def check_1KL(self):
        ''' method that checks the current Kirchhoff law at the bus '''
        sum_I = self.I
        for d in self.dres:
            sum_I += d.I
        for line in self.connections:
            if line.connections[0] == self:
                sum_I -= line.I
            else:
                sum_I += line.I
        return sum_I

class curr_inj(grid):
    def __init__(self):
        grid.__init__(self)    
                       
    def initialize(self):
        method = "B"
        if method == "A":
            # Método A. Paper ERR y AGE 
            for bus in self.buses[1:]:
                if bus.U == None:
                    bus.U = self.buses[0].U.copy()  
                if bus.Q == None:
                    bus.Q = [0, 0, 0]
                Gsum = np.zeros(4)
                Bsum = np.zeros(4)
                for line in bus.connections:
                    for line_con in line.connections:
                        if bus.ref != line_con.ref:
                            Gsum[0] += np.sum(np.real(self.Y[bus.ref*4 , :]))  #np.real(self.Y[bus.ref*4 , :])
                            Gsum[1] += np.sum(np.real(self.Y[bus.ref*4 + 1, :]))   #np.real(self.Y[bus.ref*4 + 1, line_con.ref*4 + 1])
                            Gsum[2] += np.sum(np.real(self.Y[bus.ref*4 + 2, :]))   #np.real(self.Y[bus.ref*4 + 2, line_con.ref*4 + 2])
                            Gsum[3] += np.sum(np.real(self.Y[bus.ref*4 + 3, :]))   #np.real(self.Y[bus.ref*4 + 3, line_con.ref*4 + 3])
                            Bsum[0] += np.sum(np.imag(self.Y[bus.ref*4 , :]))  #np.imag(self.Y[bus.ref*4 , line_con.ref*4])
                            Bsum[1] += np.sum(np.imag(self.Y[bus.ref*4 + 1, :]))   #np.imag(self.Y[bus.ref*4 + 1, line_con.ref*4 + 1])
                            Bsum[2] += np.sum(np.imag(self.Y[bus.ref*4 + 2, :]))   #np.imag(self.Y[bus.ref*4 + 2, line_con.ref*4 + 2])
                            Bsum[3] += np.sum(np.imag(self.Y[bus.ref*4 + 3, :]))   #np.imag(self.Y[bus.ref*4 + 3, line_con.ref*4 + 3])
                for index in range(4):
                    bus.I[index] = np.complex(0, Bsum[index])
        else:
            # Método B. Paper ERR y AGE   
            for bus in self.buses[1:]:
                if bus.U == None:
                    bus.U = self.buses[0].U.copy() 
                if bus.Q == None:
                    bus.Q = [0, 0, 0]
                for index in range(3):
                    bus.I[index] = np.complex(bus.P[index], -bus.Q[index])/np.conjugate(bus.U[index] - bus.U[3])                                   
                bus.I[3] = -np.sum(bus.I)            
            
    def generate_Y(self):
        # Y
        self.Y = np.zeros((len(self.buses)*4, len(self.buses)*4), dtype = complex)
        for bus in self.buses:
            for line in bus.connections:
                for line_con in line.connections:
                    if bus.ref != line_con.ref:
                        self.Y[bus.ref*4 : bus.ref*4 + 4, line_con.ref*4 : line_con.ref*4 + 4] = -np.linalg.inv(line.Z)
        for index in range(0, self.Y.shape[0], 4):
            aux = np.zeros([4, 4], dtype = complex)
            for index2 in range(0, self.Y.shape[1], 4):
                aux -= self.Y[index : index + 4, index2 : index2 + 4]
            self.Y[index : index + 4, index : index + 4] = aux
        for index, bus in enumerate(self.buses):
            if bus.Zg != None:
                self.Y[index*4 + 3, index*4 + 3] += 1/bus.Zg            
        # Y_B
        self.Y_B = np.zeros((self.Y.shape[0]*2, self.Y.shape[1]*2))
        for index_row in range(0, self.Y.shape[0], 4):
            for index_col in range(0, self.Y.shape[1], 4):
                self.Y_B[(index_row)*2:(index_row)*2 + 4, (index_col)*2:(index_col)*2 + 4] = np.imag(self.Y[index_row:index_row + 4, index_col:index_col + 4])
                self.Y_B[(index_row)*2:(index_row)*2 + 4, (index_col)*2 + 4:(index_col)*2 + 8] = np.real(self.Y[index_row:index_row + 4, index_col:index_col + 4])
                self.Y_B[(index_row)*2 + 4:(index_row)*2 + 8, (index_col)*2:(index_col)*2 + 4] = np.real(self.Y[index_row:index_row + 4, index_col:index_col + 4])
                self.Y_B[(index_row)*2 + 4:(index_row)*2 + 8, (index_col)*2 + 4:(index_col)*2 + 8] = - np.imag(self.Y[index_row:index_row + 4, index_col:index_col + 4])         
        
    def generate_jacobian_matrices(self):
        self.J = np.copy(self.Y_B)
        for index, bus in enumerate(self.buses):
            if bus.type == 'PQ' :
                for ph in range(3):
                    vr, vx = np.real(bus.U[ph] - bus.U[3]), np.imag(bus.U[ph] - bus.U[3])
                    ir, ix = np.real(bus.I[ph]), np.imag(bus.I[ph])
                    p, q = bus.P[ph], bus.Q[ph]
                    e = (q*(vr**2) - q*(vx**2) - 2*p*vr*vx)/(((vr**2) + (vx**2))**2)
                    f = (p*(vr**2) - p*(vx**2) + 2*q*vr*vx)/(((vr**2) + (vx**2))**2)
                    g = (-p*(vr**2) + p*(vx**2) - 2*q*vr*vx)/(((vr**2) + (vx**2))**2)
                    h = (q*(vr**2) - q*(vx**2) - 2*p*vr*vx)/(((vr**2) + (vx**2))**2)
                    self.J[index*8 + ph, index*8 + ph] -= e
                    self.J[index*8 + ph, index*8 + 3] +=e
                    self.J[index*8 + 3, index*8 + ph] += e
                    self.J[index*8 + 3, index*8 + 3] -= e
                    self.J[index*8 + ph, index*8 + 4 + ph] -= f
                    self.J[index*8 + ph, index*8 + 4 + 3] +=f
                    self.J[index*8 + 3, index*8 + 4 + ph] += f
                    self.J[index*8 + 3, index*8 + 4 + 3] -= f
                    self.J[index*8 + 4 + ph, index*8 + ph] -= g
                    self.J[index*8 + 4 + ph, index*8 + 3] +=g
                    self.J[index*8 + 4 + 3, index*8 + ph] += g
                    self.J[index*8 + 4 + 3, index*8 + 3] -= g
                    self.J[index*8 + 4 + ph, index*8 + 4 + ph] -= h
                    self.J[index*8 + 4 + ph, index*8 + 4 + 3] +=h
                    self.J[index*8 + 4 + 3, index*8 + 4 + ph] += h
                    self.J[index*8 + 4 + 3, index*8 + 4 + 3] -= h
            if bus.type == 'PV':
                next
        for index, bus in enumerate(self.buses):
            if bus.type == 'PV' :
                for index2, bus2 in enumerate(self.buses):
                    if index2 == index:
                        G = self.J[index*8 : index*8 + 4, index*8 + 4: index*8 + 8]
                        B = -self.J[index*8 + 4 : index*8 + 8, index*8 + 4: index*8 + 8]
                        self.J[index*8 : index*8 + 8, index*8 + 4: index*8 + 8] = np.zeros((8, 4))
                        self.J[index*8 : index*8 + 4, index*8 : index*8 + 4] = G
                        self.J[index*8 + 4: index*8 + 8, index*8 : index*8 + 4] = B 
                    else:
                        G = self.J[index2*8 : index2*8 + 4, index*8 + 4: index*8 + 8]
                        B = - self.J[index2*8 + 4 : index2*8 + 8, index*8 + 4: index*8 + 8]
                        self.J[index2*8 : index2*8 + 8, index*8 + 4: index*8 + 8] = np.zeros((8, 4))
                        self.J[index2*8 : index2*8 + 4, index*8 : index*8 + 4] = G
                        self.J[index2*8 + 4: index2*8 + 8, index*8 : index*8 + 4] = - B 
                
    def compute_residuals(self):
        self.U = list()
        for bus in self.buses:
            self.U += list(np.real(bus.U))
            self.U += list(np.imag(bus.U))
        self.U = np.array(self.U)
        DI = list()
        DS = list() #Lo meto yo     
        for index, bus in enumerate(self.buses):
            if bus.type == 'PQ':
                ir, ix, dpk, dqk = list(), list(), list(), list()
                for ph in range(3):
                    vr, vx = np.real(bus.U[ph] - bus.U[3]), np.imag(bus.U[ph] - bus.U[3])
                    p, q = bus.P[ph], bus.Q[ph]
                    dir = (p*vr + q*vx)/((vr**2) + (vx**2)) - np.dot(self.Y_B[index*8 + 4 + ph,:], self.U)
                    dix = (p*vx - q*vr)/((vr**2) + (vx**2)) - np.dot(self.Y_B[index*8 + ph,:], self.U)
                    ir.append(dir)   # Por fase
                    ix.append(dix)   # Por fase
                    # Residuos de potencias
                    dq = (((vr**2)+(vx**2))/((vr**2)-(vx**2))*(vr*dix - vx*dir))
                    dp = (dir*((vr**2)+(vx**2))-vx*dq)/vr
                    dpk.append(dp)
                    dqk.append(dq)
                ir.append(- np.sum(np.real(bus.I[:3])) - np.dot(self.Y_B[index*8 + 7,:], self.U) )  # Para el caso del cable neutro
                ix.append(- np.sum(np.imag(bus.I[:3])) - np.dot(self.Y_B[index*8 + 3,:], self.U) )  # Para el caso del cable neutro
                DI += ix
                DI += ir
                DS += dpk
                DS += dqk
            if bus.type == 'PV':
                ir, ix = list(), list()
                for ph in range(3):
                    vr, vx = np.real(bus.U[ph] - bus.U[3]), np.imag(bus.U[ph] - bus.U[3])
                    p = bus.P[ph]
                    ir.append( p - vr*np.real(bus.I[ph]) - vx*np.imag(bus.I[ph]) )
                    ix.append( bus.V_esp[ph]**2 - vr**2 - vx**2 )
                ir.append(- np.sum(np.real(bus.I[:3])) - np.dot(self.Y_B[index*8 + 7,:], self.U) )
                ix.append(- np.sum(np.imag(bus.I[:3])) - np.dot(self.Y_B[index*8 + 3,:], self.U) )
                DI += ix
                DI += ir
        self.DI = DI 
        self.DS = DS
        return np.max(np.abs(self.DI))      
   
    def next_step(self):
        self.DU = np.linalg.solve(self.J[8:,8:], self.DI)
        print("Residuos de tensión: {}".format(self.DU))
        print("------------------")
        self.U[8:] += self.DU
        for index, bus in enumerate(self.buses): # Updating buses voltages
            bus.U = [complex(self.U[index*8], self.U[index*8 + 4]),
                     complex(self.U[index*8 + 1], self.U[index*8 + 5]),
                     complex(self.U[index*8 + 2], self.U[index*8 + 6]),
                     complex(self.U[index*8 + 3], self.U[index*8 + 7])]      
        for line in self.lines: # Updating line currents
            line.I = np.dot(np.linalg.inv(line.Z), (np.array(line.connections[0].U) - np.array(line.connections[1].U)))
        for bus in self.buses:
            bus.I = np.zeros(4, dtype = complex)
            for line in bus.connections:
                if line.connections[0] == bus:
                    bus.I += line.I
                else:
                    bus.I -= line.I
            if bus.Zg:
                bus.I[3] += bus.U[3]/bus.Zg
            bus.I = list(bus.I)
    
    def voltage_evolution(self, iter):

        voltR = []
        voltS = []
        voltT = []
        voltN = []
        for b in self.buses: 
            voltR.append(abs(b.U[0]))
            voltS.append(abs(b.U[1]))
            voltT.append(abs(b.U[2]))
            voltN.append(abs(b.U[3]))
        self.voltages_iter[iter] = {
            "R": voltR,
            "S": voltS,
            "T": voltT,
            "N": voltN
        }
    
    def current_evolution(self, iter):

        currR = []
        currS = []
        currT = []
        currN = []
        for b in self.buses: 
            currR.append(abs(b.I[0]))
            currS.append(abs(b.I[1]))
            currT.append(abs(b.I[2]))
            currN.append(abs(b.I[3]))
        self.current_iter[iter] = {
            "R": currR,
            "S": currS,
            "T": currT,
            "N": currN
        }

    def solve(self, options):
        print('\n Solving power flow: Current Injection Method\n')
        tol, n_iter = options  
        self.generate_Y()             
        self.initialize()  
        res = 10
        iteration = 0
        self.lista_residuos = list()
        self.voltages_iter = {}
        self.current_iter = {}

        self.voltage_evolution(iteration)
        self.current_evolution(iteration)


        while res > tol and iteration < n_iter:
            print("Iteracion: " + str(iteration))
            self.generate_jacobian_matrices() 
            res = self.compute_residuals()
            #print(res)
            #res = self.res_rect()
            #print(res)
            self.next_step()
            iteration += 1
            print(f'\t Iteration: {iteration}. Residual: {res}')
            self.lista_residuos.append(res)
            
            self.voltage_evolution(iteration)
            self.current_evolution(iteration)

        for line in self.lines:
            line.I = np.linalg.solve(line.Z, (np.array(line.connections[0].U) - np.array(line.connections[1].U)) )
        self.iter_spent = iteration

class aug_rect(grid):
    def __init__(self):
        grid.__init__(self)
                       
    def initialize(self):   
        method = "B"
        if method == "A":
            # Método A. Paper ERR y AGE 
            for bus in self.buses[1:]:
                if bus.U == None:
                    bus.U = self.buses[0].U.copy()
                if bus.Q == None:
                    bus.Q = [0, 0, 0]
                Gsum = np.zeros(4)
                Bsum = np.zeros(4)
                for line in bus.connections:
                    for line_con in line.connections:
                        if bus.ref != line_con.ref:
                            Gsum[0] += np.sum(np.real(self.Y[bus.ref*4 , :]))  #np.real(self.Y[bus.ref*4 , :])
                            Gsum[1] += np.sum(np.real(self.Y[bus.ref*4 + 1, :]))   #np.real(self.Y[bus.ref*4 + 1, line_con.ref*4 + 1])
                            Gsum[2] += np.sum(np.real(self.Y[bus.ref*4 + 2, :]))   #np.real(self.Y[bus.ref*4 + 2, line_con.ref*4 + 2])
                            Gsum[3] += np.sum(np.real(self.Y[bus.ref*4 + 3, :]))   #np.real(self.Y[bus.ref*4 + 3, line_con.ref*4 + 3])
                            Bsum[0] += np.sum(np.imag(self.Y[bus.ref*4 , :]))  #np.imag(self.Y[bus.ref*4 , line_con.ref*4])
                            Bsum[1] += np.sum(np.imag(self.Y[bus.ref*4 + 1, :]))   #np.imag(self.Y[bus.ref*4 + 1, line_con.ref*4 + 1])
                            Bsum[2] += np.sum(np.imag(self.Y[bus.ref*4 + 2, :]))   #np.imag(self.Y[bus.ref*4 + 2, line_con.ref*4 + 2])
                            Bsum[3] += np.sum(np.imag(self.Y[bus.ref*4 + 3, :]))   #np.imag(self.Y[bus.ref*4 + 3, line_con.ref*4 + 3])
                for index in range(4):
                    bus.I[index] = np.complex(0, Bsum[index])
        else:
            # Método B. Paper ERR y AGE   
            for bus in self.buses[1:]:
                if bus.U == None:
                    bus.U = self.buses[0].U.copy()  
                if bus.Q == None:
                    bus.Q = [0, 0, 0]
                for index in range(3):
                    bus.I[index] = np.complex(bus.P[index], -bus.Q[index])/np.conjugate(bus.U[index] - bus.U[3])                                   
                bus.I[3] = -np.sum(bus.I)
        
    def generate_Y(self):
        # Y
        self.Y = np.zeros((len(self.buses)*4, len(self.buses)*4), dtype = complex)
        for bus in self.buses:
            for line in bus.connections:
                for line_con in line.connections:                
                        if bus.ref != line_con.ref  and hasattr(line, 'Z') == True: 
                           self.Y[bus.ref*4 : bus.ref*4 + 4, line_con.ref*4 : line_con.ref*4 + 4] += -np.linalg.inv(line.Z)                             
        for index in range(0, self.Y.shape[0], 4):
            aux = np.zeros([4, 4], dtype = complex)   
            for index2 in range(0, self.Y.shape[1], 4):
                aux -= self.Y[index : index + 4, index2 : index2 + 4]
            self.Y[index : index + 4, index : index + 4] = aux
        for index, bus in enumerate(self.buses):
            if bus.Zg != None:
                self.Y[index*4 + 3, index*4 + 3] += 1/bus.Zg 
        # Y_B
        self.Y_B = np.zeros((self.Y.shape[0]*2, self.Y.shape[1]*2), dtype = complex)
        for index_row, row in enumerate(self.Y):
            for index_col, item in enumerate(row):                
                self.Y_B[(index_row)*2, (index_col)*2] = -np.imag(item)
                self.Y_B[(index_row)*2 + 1, (index_col)*2 + 1] = np.imag(item)
                self.Y_B[(index_row)*2, (index_col)*2 + 1] = np.real(item)
                self.Y_B[(index_row)*2 + 1, (index_col)*2] = np.real(item)                                                
        self.Y_B = self.Y_B[2*4:] 
        return self.Y_B
    
    def generate_jacobian_matrices(self):
        # D_I, D_V
        self.D_I = np.zeros((self.Y.shape[0]*2, self.Y.shape[1]*2))
        self.D_V = np.zeros((self.Y.shape[0]*2, self.Y.shape[1]*2))                
        for bus in self.buses:            
             epsilon = 1 if bus.type == 'PQ' else 0                         
             for pointer, item in enumerate(bus.I[:-1]):                
                self.D_I[(bus.ref)*8 + pointer*2, (bus.ref)*8 + pointer*2] = np.imag(item)
                self.D_I[(bus.ref)*8 + pointer*2, (bus.ref)*8 + pointer*2 + 1] = np.real(item)
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2] = np.real(item)*epsilon
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2 + 1] = -np.imag(item)*epsilon
                self.D_I[(bus.ref)*8 + pointer*2, (bus.ref)*8 + 6] = -np.imag(item)
                self.D_I[(bus.ref)*8 + pointer*2, (bus.ref)*8 + 7] = -np.real(item)
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + 6] = -np.real(item)*epsilon
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + 7] = np.imag(item)*epsilon                                 
             for pointer, item in enumerate(bus.U[:-1]):
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2] += (1-epsilon)*2*(np.imag(item) - np.imag(bus.U[-1]))
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2 + 1] += (1-epsilon)*2*(np.real(item) - np.real(bus.U[-1]))
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + 6] += -(1-epsilon)*2*(np.imag(item) - np.imag(bus.U[-1]))  
                self.D_I[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + 7] += -(1-epsilon)*2*(np.real(item) - np.real(bus.U[-1]))  
             for pointer, item in enumerate(bus.U[:-1]):                                      
                self.D_V[(bus.ref)*8 + pointer*2, (bus.ref)*8 + pointer*2] = np.real(item) - np.real(bus.U[-1])
                self.D_V[(bus.ref)*8 + pointer*2, (bus.ref)*8 + pointer*2 + 1] = np.imag(item) - np.imag(bus.U[-1])
                self.D_V[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2] = epsilon*(np.imag(item) - np.imag(bus.U[-1]))
                self.D_V[(bus.ref)*8 + pointer*2 + 1, (bus.ref)*8 + pointer*2 + 1] = -epsilon*(np.real(item) - np.real(bus.U[-1]))                    
                self.D_V[(bus.ref)*8 + 6:(bus.ref)*8 + 8, (bus.ref)*8 + pointer*2:(bus.ref)*8 + pointer*2 + 2] = np.eye(2)
                self.D_V[(bus.ref)*8 + 6:(bus.ref)*8 + 8, (bus.ref)*8 + 6:(bus.ref)*8 + 8] = np.eye(2)    
        self.D_I = self.D_I[2*4:,2*4:] 
        self.D_V = self.D_V[2*4:,2*4:]         
        return self.D_I, self.D_V
                   
    def compute_residuals(self):
        U = list()
        I = list()
        res_S = list()     
        for item in self.buses[0].U:
            U.append(np.imag(item))
            U.append(np.real(item))
        for bus in self.buses[1:]:                        
            for item in bus.U:
                U.append(np.imag(item))
                U.append(np.real(item))   
            for item in bus.I:
                I.append(np.real(item))
                I.append(np.imag(item))
            if bus.type == 'PQ':
                for index in range(3):              
                    res_S.append(bus.P[index] - np.real(bus.U[index] - bus.U[3])*np.real(bus.I[index]) - np.imag(bus.U[index] - bus.U[3])*np.imag(bus.I[index]))                     
                    res_S.append(bus.Q[index] - np.imag(bus.U[index] - bus.U[3])*np.real(bus.I[index]) + np.real(bus.U[index] - bus.U[3])*np.imag(bus.I[index]))                                
                res_S.append(0)
                res_S.append(0)                                
            if bus.type == 'PV':                                
                for index in range(3):                
                    res_S.append(bus.P[index] - np.real(bus.U[index] - bus.U[3])*np.real(bus.I[index])-np.imag(bus.U[index] - bus.U[3])*np.imag(bus.I[index])) 
                    res_S.append(bus.V_esp[index]**2-(np.real(bus.U[index] - bus.U[3]))**2-(np.imag(bus.U[index] - bus.U[3]))**2)
                res_S.append(0)
                res_S.append(0)        
        res_I = I - np.dot(self.Y_B, U)                   
        res_S = np.array(res_S, dtype = complex)   
        #residual = np.concatenate((res_I, res_S))      
        self.residual_S = np.concatenate([res_S], axis=0)
        self.residual_I = np.concatenate([res_I], axis=0)  
        self.residual = np.concatenate([res_I, res_S], axis=0)   
        self.res_ = np.copy(self.residual)
        return np.max(np.abs(self.residual))               
    
    def next_step(self):
        Y_bus = self.generate_Y()
        Y_bus = Y_bus[:,2*4:]
        D_I, D_V = self.generate_jacobian_matrices()
        res = self.compute_residuals()        
        self.J = np.block([[Y_bus, -np.eye(D_V.shape[0], D_V.shape[1])], [D_I, D_V]])
        delta = np.linalg.solve(self.J, self.residual)                     
        delta_U = delta[:(len(self.buses)-1)*8]
        delta_I = delta[(len(self.buses)-1)*8:]
        print("Residuos de tensión: {}".format(delta_U))
        print("------------------")
        index = 0
        for bus in self.buses[1:]:
            for index2 in range(len(bus.U)):
                bus.U[index2] += np.complex(delta_U[index + 1], delta_U[index])
                index += 2
        index = 0
        for bus in self.buses[1:]:
            for index2 in range(len(bus.U)):
                bus.I[index2] += np.complex(delta_I[index], delta_I[index + 1])
                index += 2                     
        return delta, delta_U, delta_I, self.J

    def voltage_evolution(self, iter):

        voltR = []
        voltS = []
        voltT = []
        voltN = []
        for b in self.buses: 
            voltR.append(abs(b.U[0]))
            voltS.append(abs(b.U[1]))
            voltT.append(abs(b.U[2]))
            voltN.append(abs(b.U[3]))
        self.voltages_iter[iter] = {
            "R": voltR,
            "S": voltS,
            "T": voltT,
            "N": voltN
        }
    
    def current_evolution(self, iter):

        currR = []
        currS = []
        currT = []
        currN = []
        for b in self.buses: 
            currR.append(abs(b.I[0]))
            currS.append(abs(b.I[1]))
            currT.append(abs(b.I[2]))
            currN.append(abs(b.I[3]))
        self.current_iter[iter] = {
            "R": currR,
            "S": currS,
            "T": currT,
            "N": currN
        }

    def solve(self, options):
        print('\n Solving power flow: Augmented Rectangular Method\n')
        tol, n_iter = options        
        self.generate_Y()
        self.initialize()
        res = 10
        iteration = 0        
        self.x =list()
        self.voltages_iter = {}
        self.current_iter = {}
        self.lista_residuos = list()    

        self.voltage_evolution(iteration)
        self.current_evolution(iteration)

        while res > tol and iteration < n_iter:
            print("Iteración: " + str(iteration))
            self.generate_Y()
            self.generate_jacobian_matrices()
            res = self.compute_residuals()
            self.next_step()
            iteration += 1
            print('\t Iteration: ' + str(iteration) + '. Residual: ' + str(res))
            self.x.append(iteration)
            self.lista_residuos.append(res)
            self.voltage_evolution(iteration)
            self.current_evolution(iteration)

        for line in self.lines:
            line.I = np.dot(np.linalg.inv(line.Z), (np.array(line.connections[0].U) - np.array(line.connections[1].U)))        
        self.iter_spent = iteration
        
        return self.lista_residuos
    
   

        