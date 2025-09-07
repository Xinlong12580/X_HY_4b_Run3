import glob

files = glob.glob("*.log")

print(files)
massXs = []
massYs = []
effs = {"1p0": [], "2p0": [], "0p2": [], "0p1": [] , "1p1": [], "2p1": [], "1p2": [], "2p2": []}
for _file in files:
    if "condor" in _file or "FAILED" in _file:
        continue
    print(_file)
    mass = _file.partition("__")[0]
    mx = mass.partition("_")[0]
    my = mass.partition("_")[2]
    massXs.append(mx)
    massYs.append(my)
    with open(_file, "r") as f:
        lines = f.readlines()
        effs["1p0"].append(lines[-8].strip().split()[1])
        effs["2p0"].append(lines[-7].strip().split()[1])
        effs["0p2"].append(lines[-6].strip().split()[1])
        effs["0p1"].append(lines[-5].strip().split()[1])
        effs["1p1"].append(lines[-4].strip().split()[1])
        effs["2p1"].append(lines[-3].strip().split()[1])
        effs["1p2"].append(lines[-2].strip().split()[1])
        effs["2p2"].append(lines[-1].strip().split()[1])
with open ("matching_eff_withPNet.txt", "w") as f:
    for i in range(len(massXs)):
        f.write(f"{massXs[i]} {massYs[i]} {effs['1p0'][i]} {effs['2p0'][i]} {effs['0p2'][i]} {effs['0p1'][i]} {effs['1p1'][i]} {effs['2p1'][i]} {effs['1p2'][i]} {effs['2p2'][i]}\n") 
