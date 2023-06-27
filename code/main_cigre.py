import numpy as np
import pf_lib as pf
import matplotlib.pyplot as plt


U_ref = [complex(400/np.sqrt(3)*np.cos(0*np.pi/180), 400/np.sqrt(3)*np.sin(0*np.pi/180)),
         complex(400/np.sqrt(3)*np.cos(-120*np.pi/180), 400/np.sqrt(3)*np.sin(-120*np.pi/180)),
         complex(400/np.sqrt(3)*np.cos(120*np.pi/180), 400/np.sqrt(3)*np.sin(120*np.pi/180)),
         0]
tol, n_iter_max = 1e-5, 120
options = [tol, n_iter_max]  
 
Rg = 3
Rg_500 = None
Deseq = {'R2' : [20/100, 20/100, 60/100],
         'R11': [30/100, 20/100, 30/100],
         'R15': [40/100, 30/100, 30/100],
         'R16': [40/100, 10/100, 50/100],
         'R17': [35/100, 25/100, 40/100],
         'R18': [40/100, 20/100, 40/100]}
V_esp = [231,231,231]  


net = pf.curr_inj()
net.add_bus(0, P = None, Q = None, U = U_ref, Zg = 0.01, name = 'Slack')    
net.add_bus(1, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500)
net.add_bus(2, P = list(-12e3*0.95*np.array(Deseq['R2'])), Q = list(-12e3*np.sin(np.arccos(0.95))*np.array(Deseq['R2'])), U = None, Zg = Rg) 
net.add_bus(3, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500) 
net.add_bus(4, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg) 
net.add_bus(5, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500) 
net.add_bus(6, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg) 
net.add_bus(7, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500) 
net.add_bus(8, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg) 
net.add_bus(9, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500)
net.add_bus(10, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg) 
net.add_bus(11, P = list(-55e3*0.95*np.array(Deseq['R11'])), Q = list(-55e3*np.sin(np.arccos(0.95))*np.array(Deseq['R11'])), U = None, Zg = Rg) 
net.add_bus(12, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500) 
#net.add_bus(13, P = [100e3,100e3,100e3], Q = None, U = None, Zg = Rg_500, V_esp = V_esp) 
net.add_bus(13, P = [100e3,100e3,100e3], Q = list(-25e3*np.sin(np.arccos(0.95))*np.array(Deseq['R15'])), U = None, Zg = Rg) 
net.add_bus(14, P = [0,0,0], Q = [0,0,0], U = None, Zg = Rg_500) 
net.add_bus(15, P = list(-25e3*0.95*np.array(Deseq['R15'])), Q = list(-25e3*np.sin(np.arccos(0.95))*np.array(Deseq['R15'])), U = None, Zg = Rg) 
net.add_bus(16, P = list(-100e3*0.95*np.array(Deseq['R16'])), Q = list(-100e3*np.sin(np.arccos(0.95))*np.array(Deseq['R16'])), U = None, Zg = Rg) 
net.add_bus(17, P = list(-44e3*0.95*np.array(Deseq['R17'])), Q = list(-44e3*np.sin(np.arccos(0.95))*np.array(Deseq['R17'])), U = None, Zg = Rg) 
net.add_bus(18, P = list(-10e3*0.95*np.array(Deseq['R18'])), Q = list(-10e3*np.sin(np.arccos(0.95))*np.array(Deseq['R18'])), U = None, Zg = Rg) 


net.add_line('UG1', 0.5,  0,  1)
net.add_line('UG1', 35,  1,  2)
net.add_line('UG1', 35,  2,  3)
net.add_line('UG1', 35,  3,  4)
net.add_line('UG1', 35,  4,  5)
net.add_line('UG1', 35,  5,  6)
net.add_line('UG1', 35,  6,  7)
net.add_line('UG1', 35,  7,  8)
net.add_line('UG1', 35,  8,  9)
net.add_line('UG1', 35,  9,  10)
net.add_line('UG3', 30,  3,  11)
net.add_line('UG3', 35,  4,  12)
net.add_line('UG3', 35,  12, 13)
net.add_line('UG3', 35,  13, 14)
net.add_line('UG3', 30,  14, 15)
net.add_line('UG3', 30,  6,  16)
net.add_line('UG3', 30,  9,  17)
net.add_line('UG3', 30,  10, 18)

net.solve(options)

# Comprobaciones
print('')
print('1KL:')
for bus in net.buses[1:]:
    I = np.copy(bus.I)
    if bus.Zg != None:
        I[3] -= bus.U[3]/bus.Zg
    for line in bus.connections:
        if line.connections[0] == bus:
            I -= line.I
        else:
            I += line.I
    print(f'\t Bus {bus.ref}: {np.abs(I)}')

print('I - YV:')
I = list()
U = list(np.copy(net.buses[0].U))
for bus in net.buses[1:]:
    I += bus.I
    U += bus.U
res = np.array(I) - np.dot(net.Y[4:,:], np.array(U))
print(f'\t {np.max(np.abs(res))}')

print('PQ-PV:')
for bus in net.buses[1:]:
    if bus.type == 'PQ':         
        res = list(np.array([complex(item[0], item[1]) for item in zip(bus.P, bus.Q)]) - np.array([bus.U[0]-bus.U[3], bus.U[1]-bus.U[3], bus.U[2]-bus.U[3]])*np.array(np.conj(bus.I[:3])))
        print(f'\t PQ: {np.abs(res)}')
    if bus.type == 'PV':
        res = list(np.array(bus.V_esp) - np.abs(np.array([bus.U[0]-bus.U[3], bus.U[1]-bus.U[3], bus.U[2]-bus.U[3]]))) 
        print(f'\t PV: {np.abs(res)}')

print('Jacobian matrix condition number')
nc = np.linalg.cond(net.J)
print('Condition number of J is: {}'.format(np.round(nc,3)))







