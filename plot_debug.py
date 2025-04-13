import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle

#-----------------------------------loading files for the templates --------------------------------------------
with open("debug_data.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_skim/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
var_columns = ["leadingFatJetPt", "leadingFatJetPhi", "leadingFatJetEta", "leadingFatJetMsoftdrop"]
bins = {}
bin_centers = {}
bins["leadingFatJetPt"] = np.linspace(0, 3000, 101)

bins["leadingFatJetPhi"] = np.linspace(-np.pi, np.pi , 21)

bins["leadingFatJetEta"] = np.linspace(-3, 3, 21)

bins["leadingFatJetMsoftdrop"] = np.linspace(0, 1500, 51)
for column in var_columns:
    bin_centers[column] = 0.5 * (bins[column][:-1] + bins[column][1:])
#MC_weight = "lumiXsecWeight"
MC_weight = "genWeight"
mplhep.style.use("CMS")

year = "2022"
processes = {"MC_QCDJets": ["QCD-4Jets_HT-100to200"], "MC_HiggsJets": ["WplusH_Hto2B_Wto2Q_M-125"],}


#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling
h_BKGs = {}
BKG_fileWeight = {}
BKG_idxs = {}
BKG_totalWeight = {}

for process in processes:
    h_BKGs[process] = {}
    BKG_fileWeight[process] = {}
    BKG_idxs[process] = {}
    BKG_totalWeight[process] = {}
    for subprocess in processes[process]:
        if subprocess == "*":
            if "SignalMC_" in process:
                for _subprocess in signal_json["2022"][process]:
                    BKG_fileWeight[process][_subprocess] = []
                    BKG_idxs[process][_subprocess] = 0
                    BKG_totalWeight[process][_subprocess] = 0
                    h_BKGs[process][_subprocess] = {}
                    for column in var_columns:
                        h_BKGs[process][_subprocess][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
                break
            elif "MC_" in process:
                for _subprocess in Xsec_json[process]:
                    BKG_fileWeight[process][_subprocess] = []
                    BKG_idxs[process][_subprocess] = 0
                    BKG_totalWeight[process][_subprocess] = 0
                    h_BKGs[process][_subprocess] = {}
                    for column in var_columns:
                        h_BKGs[process][_subprocess][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
                break
        else:
            BKG_fileWeight[process][subprocess] = []
            BKG_idxs[process][subprocess] = 0
            BKG_totalWeight[process][subprocess] = 0
            h_BKGs[process][subprocess] = {}
            for column in var_columns:
                h_BKGs[process][subprocess][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
            
print(BKG_totalWeight)
# loading weight info
print("Loading Weight")

for data_file in data_files:
    for process in BKG_fileWeight:
        if process in data_file:
            for subprocess in BKG_fileWeight[process]:
                if subprocess in data_file:
                    print(data_file)
                    rdf_np = ROOT.RDataFrame("Runs", data_file).AsNumpy(["genEventSumw"])
                    BKG_fileWeight[process][subprocess].append(sum(rdf_np["genEventSumw"]))
                    #BKG_fileWeight[process][subprocess].append(ROOT.RDataFrame("Runs", data_file).Sum("genEventSumw").GetValue())
for process in BKG_fileWeight:
    for subprocess in BKG_fileWeight[process]:
        BKG_totalWeight[process][subprocess] = sum(BKG_fileWeight[process][subprocess])

print("Loading BKG")

lumi = lumi_json[year]

# making templates
for data_file in data_files:
    for process in h_BKGs:
        if process in data_file:
            for subprocess in h_BKGs[process]:
                if subprocess in data_file:
                    print(data_file)
                    if "SignalMC_" in process:
                        Xsec = 1
                    elif "MC_" in process:
                        Xsec = Xsec_json[process][subprocess]
                    rdf = ROOT.RDataFrame("Events", data_file)
                    rdf = rdf.Filter("SkimFlag == 2 || SkimFlag == 3")
                    if rdf.Count().GetValue() < 1:
                        print("Empty File")
                    else:
                        rdf = rdf.Define("leadingFatJetPt", "FatJet_pt[0]")
                        rdf = rdf.Define("leadingFatJetPhi", "FatJet_phi[0]")
                        rdf = rdf.Define("leadingFatJetEta", "FatJet_eta[0]")
                        rdf = rdf.Define("leadingFatJetMsoftdrop", "FatJet_msoftdrop[0]")
                        rdf_np = rdf.AsNumpy(var_columns + [MC_weight])
                        if "MC" in process:
                            for i in range(len(rdf_np["leadingFatJetPt"])):
                                #if rdf_np["leadingFatJetPt"][i] > 880 and rdf_np["leadingFatJetPt"][i] < 920:
                                if rdf_np["genWeight"][i] > 880:
                                    print(rdf_np["leadingFatJetPt"][i])
                                    print(rdf_np["genWeight"][i])
                        for column in var_columns:
                            #h_BKGs[process][subprocess][column].fill(BKG = rdf_np[column], weight = (rdf_np[MC_weight] * BKG_fileWeight[process][subprocess][BKG_idxs[process][subprocess]] / BKG_totalWeight[process][subprocess]) )                
                            h_BKGs[process][subprocess][column].fill(BKG = rdf_np[column], weight = (rdf_np[MC_weight] * lumi * Xsec / BKG_totalWeight[process][subprocess]) )                
                    BKG_idxs[process][subprocess] += 1

with open("hist_BKGs_debug.pkl", "wb") as f:
    pickle.dump(h_BKGs, f)

print("LOADING BKG SUCCESSFUL")


#--------------------- extracting interested processes-----------------------------------------------
h_QCD = {}
h_Higgs = {}
for column in var_columns:
    h_QCD[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Higgs[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
for subprocess in h_BKGs["MC_QCDJets"]:
    for column in var_columns:
        h_QCD[column] += h_BKGs["MC_QCDJets"][subprocess][column]


for subprocess in h_BKGs["MC_HiggsJets"]:
    for column in var_columns:
        h_Higgs[column] += h_BKGs["MC_HiggsJets"][subprocess][column]




#-------------------------------Ploting -----------------------------------------------------------

with open("raw_nano/CMS_style.json") as f:
    CMS_style = json.load(f)
colors = CMS_style["color"]
for column in var_columns:
    h_QCD[column].label = "QCD"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    mplhep.histplot(
        [h_Higgs[column], h_QCD[column] ],
        label = ["Higgs Wplus", "QCD HT100-200"],
        color = [ "red", "orange"],
        stack = True,
        histtype = "fill",
        ax = ax1,
    )
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(1,10000000)
    ax1.set_ylabel("Event Counts")
    ax1.set_xlabel("")
    ax1.legend()
    ax1.set_xlabel(column)

    fig.tight_layout()
    fig.savefig(f"test_debug_{column}.png")
    
