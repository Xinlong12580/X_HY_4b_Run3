import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle

#-----------------------------------loading files for the templates --------------------------------------------
with open("test_data.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
var_columns = ["leadingFatJetPt", "leadingFatJetPhi", "leadingFatJetEta"]
bins = {}
bin_centers = {}
bins["leadingFatJetPt"] = np.linspace(0, 2000, 51)
bins["leadingFatJetPhi"] = np.linspace(-np.pi, np.pi , 21)
bins["leadingFatJetEta"] = np.linspace(-3, 3, 21)
for column in var_columns:
    bin_centers[column] = 0.5 * (bins[column][:-1] + bins[column][1:])
#MC_weight = "lumiXsecWeight"
MC_weight = "genWeight"
mplhep.style.use("CMS")

year = "2022"
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"]}
#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
h_data = {}
for column in var_columns:
    h_data[column] = Hist.new.Var(bins[column], name="data", label="Data").Double()
for data_file in data_files:
    if "JetMET" in data_file:
        print(data_file)
        rdf_np = ROOT.RDataFrame("Events", data_file).AsNumpy(var_columns)
        for column in var_columns:
            h_data[column].fill(rdf_np[column])

data_binned = {}
data_binned_error = {}
for column in var_columns:
    data_binned[column] = h_data[column].values()
    data_binned_error[column] = np.sqrt((h_data[column].variances()))  # sqrt(N)

with open("hist.pkl", "wb") as f:
    pickle.dump(h_data, f)

print("Loading data successful")

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
                    Xsec = Xsec_json[process][subprocess]
                    rdf = ROOT.RDataFrame("Events", data_file)
                    if rdf.Count().GetValue() < 1:
                        print("Empty File")
                    else:
                        rdf_np = rdf.AsNumpy(var_columns + [MC_weight])
                        for column in var_columns:
                            #h_BKGs[process][subprocess][column].fill(BKG = rdf_np[column], weight = (rdf_np[MC_weight] * BKG_fileWeight[process][subprocess][BKG_idxs[process][subprocess]] / BKG_totalWeight[process][subprocess]) )                
                            h_BKGs[process][subprocess][column].fill(BKG = rdf_np[column], weight = (rdf_np[MC_weight] * lumi * Xsec / BKG_totalWeight[process][subprocess]) )                
                    BKG_idxs[process][subprocess] += 1

with open("hist.pkl", "ab") as f:
    pickle.dump(h_BKGs, f)

print("LOADING BKG SUCCESSFUL")
#--------------------- extracting interested processes-----------------------------------------------
h_QCD = {}
h_WZ = {}
h_Higgs = {}
h_TTBar = {}
h_All = {}
ratio = {}
ratio_error = {}
for column in var_columns:
    h_QCD[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_WZ[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Higgs[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_TTBar[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_All[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    ratio[column] = []
    ratio_error[column] = []
for subprocess in h_BKGs["MC_QCDJets"]:
    for column in var_columns:
        h_QCD[column] += h_BKGs["MC_QCDJets"][subprocess][column]

for subprocess in h_BKGs["MC_WZJets"]:
    for column in var_columns:
        h_WZ[column] += h_BKGs["MC_WZJets"][subprocess][column]



for subprocess in h_BKGs["MC_HiggsJets"]:
    for column in var_columns:
        h_Higgs[column] += h_BKGs["MC_HiggsJets"][subprocess][column]

for subprocess in h_BKGs["MC_TTBarJets"]:
    for column in var_columns:
        h_TTBar[column] += h_BKGs["MC_TTBarJets"][subprocess][column]

for column in var_columns:
    h_All[column] =  h_QCD[column] + h_WZ[column] + h_TTBar[column] + h_Higgs[column]
    ratio[column] = [x / y for x,y in zip(data_binned[column], h_All[column].values())]
    ratio_error[column] = [x / y for x,y in zip(data_binned_error[column], h_All[column].values())]
#-------------------------------Ploting -----------------------------------------------------------

with open("raw_nano/CMS_style.json") as f:
    CMS_style = json.load(f)
colors = CMS_style["color"]
for column in var_columns:
    h_QCD[column].label = "QCD"
    h_WZ[column].label = "WZ"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax1.errorbar(bin_centers[column], data_binned[column], yerr=data_binned_error[column], fmt='o', color='black', label='Data')
    mplhep.histplot(
        [h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        label = ["Higgs", "TTBar", "WZ", "QCD"],
        color = ["red", "lightblue", "green", "orange"],
        stack = True,
        histtype = "fill",
        ax = ax1,
    )
    mplhep.histplot(
        [h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1,
        linewidth = 1.2,
    )
    #mplhep.histplot(h_QCD[column], yerr=False, histtype="step", label="QCD", ax = ax1)
    #mplhep.histplot(h_WZ[column], yerr=False, histtype="step", label="WZ", ax = ax1)
    #mplhep.histplot(h_Higgs[column], yerr=False, histtype="step", label="Higgs", ax = ax1)
    #mplhep.histplot(h_TTBar[column], yerr=False, histtype="step", label="TTBar", ax = ax1)
    #mplhep.histplot(h_All[column], yerr=False, histtype="step", label="All MC", ax = ax1)
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(1,10000000)
    ax1.set_ylabel("Event Counts")
    ax1.set_xlabel(column)
    ax1.legend()

    ax2.errorbar(bin_centers[column], ratio[column], yerr=ratio_error[column], fmt='o', color='black', label='Data')
    ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
    ax2.set_ylabel("Data/MC")
    ax2.set_ylim(0, 2)

    plt.tight_layout()
    plt.savefig(f"test_new_{column}.png")
