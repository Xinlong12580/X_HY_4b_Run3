import matplotlib.pyplot as plt
import ROOT
import os
import mplhep as hep

from argparse import ArgumentParser

parser=ArgumentParser()

parser.add_argument('--mode', type=str, action='store', default = "1p1", required=False)
args = parser.parse_args()

plt.style.use(hep.style.CMS)
with open(f"outputList/output_limits_{args.mode}.txt", "r") as f:
    files = [file.strip() for file in f.readlines() if "AsymptoticLimits" in file]
print(files)
save_dir = f"plots/plots_limits_{args.mode}" 
Limits = {}
for file in files:
    f = ROOT.TFile.Open(file)
    tree = f.limit
    limit = []
    for entry in tree:
        limit.append(tree.limit)
    if limit[2] > 1000:
        continue
    M_i_ind = file.find("123456_") + 7
    M_f_ind = file.find("_SB")
    M_str = file[M_i_ind: M_f_ind]
    MX = int(M_str.partition("_")[0])
    MY = int(M_str.partition("_")[2])
    if MY not in Limits:
        Limits[MY] = {}
    Limits[MY][MX] = limit
print(Limits)

for MY in Limits:
    MXs = []
    P2sigmas = []
    P1sigmas = []
    Medians = []
    M1sigmas = []
    M2sigmas = []
    for MX in Limits[MY]:
        MXs.append(MX)
    MXs.sort()    
    for MX in MXs:
        P2sigmas.append(Limits[MY][MX][0])
        P1sigmas.append(Limits[MY][MX][1])
        Medians.append(Limits[MY][MX][2])
        M1sigmas.append(Limits[MY][MX][3])
        M2sigmas.append(Limits[MY][MX][4])
    print(MXs)
    print(P2sigmas)
    print(P1sigmas)
    print(Medians)
    print(M1sigmas)
    print(M2sigmas)
    fig = plt.figure(figsize = (10, 8)) 
    ax = fig.add_subplot(1, 1, 1)
    ax.fill_between(MXs, M2sigmas, P2sigmas, color = "yellow", label = "95% expected")
    ax.fill_between(MXs, M1sigmas, P1sigmas, color = "green", label = "68% expected", zorder=3)

    ax.plot(MXs, Medians, color='k', marker='o', label = "Expected", zorder=10)
    ax.set_title(f"XHY4b_{args.mode}_limit_MY: {MY} GeV")
    ax.set_xlabel("MX(GeV)")
    ax.set_ylabel("cross section x branching ratio(fb)")
    ax.legend(loc = 1)
    fig.savefig(f"{save_dir}/linear_limits_{args.mode}_{MY}.png")
    ax.set_yscale("log")
    fig.savefig(f"{save_dir}/log_limits_{args.mode}_{MY}.png")




