import os

import pandas as pd


ct = []
n = []
for i in os.listdir():
    if "ct" in i:
        d = pd.read_csv(os.path.join(i, "loads.csv"))
        ct.append(i)
        n.append(len(d))
data = pd.DataFrame({"ct": ct, "cups": n})