import pickle
import numpy as np
import matplotlib.pyplot as plt

#--------------------------------defining parameters---------------------------------------------------------
cuts = [ "Region_VB1", "BeforeSkim", "Skim", "GoldenJson", "SkimOf1p1", "LeptonVeto", "TriggerCut", "FlagCut", "FatJetID", "FatJetPt", "FatJetMass", "DeltaEta", "MassJJ", "HiggsMatch", "Region_VB1"]
cutflows = {}
years = ["2022", "2022EE", "2023", "2023BPix"]
for cut in cuts:
    cutflows[cut] = {}
    for year in years:
        cutflows[cut][year] = {}
MC_weight = "genWeight"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
colors = {"data": "black", "MC_QCDJets": "red", "MC_WZJets": "blue", "MC_HiggsJets": "yellow", "MC_TTBarJets": "green", "MC_DibosonJets": "purple", "MC_SingleTopJets": "lightblue", "SignalMC_XHY4b": "beige"}
with open("pkls/hists_division_1p1_cutflow.pkl", "rb") as f:
    cutflows = pickle.load(f)
save_dir = "plots/plots_division_1p1_cutflow"
#------------------------------ making plots ------------------------------------------------------------
#plotting individually
for year in years:
    fig = plt.figure(figsize = (20,12))
    ax = fig.add_subplot(1, 1, 1)
    x = np.arange(len(cuts))
    width = 0.3
    for process in cutflows["Skim"][year]:
        bars = np.zeros(len(cuts))
        for i in range(len(cuts)):
            cut = cuts[i]
            n = 0
            if process == "data":
                n += cutflows[cut][year][process]
            else:
                for subprocess in cutflows[cut][year][process]:
                    n += cutflows[cut][year][process][subprocess]
            bars[i] = n
        print(bars)
        ax.bar(x - width/2, bars, width, edgecolor = colors[process], facecolor = "none", label = process  ) 
        
    ax.set_ylabel("Events")
    ax.set_title(f"{year} Cutflow")
    ax.set_xticks(x)
    ax.set_xticklabels(cuts, rotation=45, ha='right')
    ax.set_yscale("log")
    ax.legend()
    fig.savefig(f"{save_dir}/{year}_cutflow.png")

#plotting S/sqrt(B)
for year in years:
    fig = plt.figure(figsize = (20,12))
    ax = fig.add_subplot(1, 1, 1)
    x = np.arange(len(cuts))
    width = 0.3
    counts_S = np.zeros(len(cuts))
    counts_B = np.zeros(len(cuts))
    for i in range(len(cuts)):
        n_B = 0
        n_S = 0
        cut = cuts[i]
        for process in cutflows[cut][year]:
            if process == "data":
                continue
            for subprocess in cutflows[cut][year][process]:
                if "Signal" in process:
                    n_S += cutflows[cut][year][process][subprocess]
                else:
                    n_B += cutflows[cut][year][process][subprocess]
        counts_B[i] = n_B
        counts_S[i] = n_S
    for S,B in zip(counts_S, counts_B):
        print(S, B) 
    print(type(n_B))
    bars = [S / np.sqrt(B) for S,B in zip(counts_S, counts_B)]   
    ax.bar(x - width/2, bars, width, label = process  ) 
        
    ax.set_ylabel("S/sqrt(B)")
    ax.set_title(f"{year} Cutflow")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(cuts, rotation=45, ha='right')
    ax.legend()
    fig.savefig(f"{save_dir}/{year}_SoverSqrtB.png")

#plotting S/sqrt(B)






