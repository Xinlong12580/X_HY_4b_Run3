import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle
with open("test_data.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection/" + line.strip()) for line in lines]

with open("raw_nano/Xsections_background.json") as f:
    bkg_json = json.load(f)

with open("hist_data.pkl", "rb") as f:
    h_data = pickle.load(f)
with open("hist_BKGs.pkl", "rb") as f:
    h_BKGs = pickle.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------

var_columns = ["leadingFatJetPt", "leadingFatJetPhi", "leadingFatJetEta", "leadingFatJetMsoftdrop", "MassLeadingTwoFatJets", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "PtYCandidate", "EtaYCandidate", "PhiYCandidate"]
bins = {}
bin_centers = {}
bins["leadingFatJetPt"] = np.linspace(0, 3000, 101)
bins["PtHiggsCandidate"] = np.linspace(0, 3000, 101)
bins["PtYCandidate"] = np.linspace(0, 3000, 101)

bins["leadingFatJetPhi"] = np.linspace(-np.pi, np.pi , 21)
bins["PhiHiggsCandidate"] = np.linspace(-np.pi, np.pi , 21)
bins["PhiYCandidate"] = np.linspace(-np.pi, np.pi , 21)

bins["leadingFatJetEta"] = np.linspace(-3, 3, 21)
bins["EtaHiggsCandidate"] = np.linspace(-3, 3, 21)
bins["EtaYCandidate"] = np.linspace(-3, 3, 21)

bins["leadingFatJetMsoftdrop"] = np.linspace(0, 1500, 51)
bins["MassLeadingTwoFatJets"] = np.linspace(0, 5000, 201)
bins["MassHiggsCandidate"] = np.linspace(0, 1500, 51)
bins["MassYCandidate"] = np.linspace(0, 1500, 51)

for column in var_columns:
    bin_centers[column] = 0.5 * (bins[column][:-1] + bins[column][1:])
#MC_weight = "lumiXsecWeight"
MC_weight = "genWeight"
mplhep.style.use("CMS")

year = "2022"
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}

data_binned = {}
data_binned_error = {}
for column in var_columns:
    data_binned[column] = h_data[column].values()
    data_binned_error[column] = np.sqrt((h_data[column].variances()))  # sqrt(N)
#--------------------- extracting interested processes-----------------------------------------------
h_QCD = {}
h_WZ = {}
h_Higgs = {}
h_TTBar = {}
h_Diboson = {}
h_SingleTop = {}
h_Signal = {}
h_All = {}
ratio = {}
ratio_error = {}
for column in var_columns:
    h_QCD[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_WZ[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Higgs[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_TTBar[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Diboson[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_SingleTop[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Signal[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
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

for subprocess in h_BKGs["MC_DibosonJets"]:
    for column in var_columns:
        h_Diboson[column] += h_BKGs["MC_DibosonJets"][subprocess][column]

for subprocess in h_BKGs["MC_SingleTopJets"]:
    for column in var_columns:
        h_SingleTop[column] += h_BKGs["MC_SingleTopJets"][subprocess][column]

for subprocess in h_BKGs["SignalMC_XHY4b"]:
    for column in var_columns:
        h_Signal[column] += h_BKGs["SignalMC_XHY4b"][subprocess][column]

for column in var_columns:
    h_All[column] =  h_QCD[column] + h_WZ[column] + h_TTBar[column] + h_Higgs[column] + h_Diboson[column] + h_SingleTop[column]
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
        [h_SingleTop[column], h_Diboson[column], h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
        color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
        stack = True,
        histtype = "fill",
        ax = ax1,
    )
    mplhep.histplot(
        [h_SingleTop[column], h_Diboson[column], h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1,
        linewidth = 1.2,
    )
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(1,10000000)
    ax1.set_ylabel("Event Counts")
    ax1.set_xlabel("")
    ax1.legend()

    ax2.errorbar(bin_centers[column], ratio[column], yerr=ratio_error[column], fmt='o', color='black', label='Data')
    ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
    ax2.set_ylabel("Data/MC")
    ax2.set_ylim(0, 2)
    ax2.set_xlabel(column)

    fig.tight_layout()
    fig.savefig(f"test_new_{column}.png")
    
    #----plotting signal------

    fig_s, (ax1_s, ax2_s) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    mplhep.histplot(
        [h_Signal[column] ],
        label = ["Signal MX-3000_MY-300"],
        color = ["purple"],
        stack = True,
        histtype = "fill",
        ax = ax1_s,
    )
    mplhep.histplot(
        [h_Signal[column] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1_s,
        linewidth = 1.2,
    )
    
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1_s)
    ax1_s.set_yscale("log")
    ax1_s.set_ylim(1,10000000)
    ax1_s.set_ylabel("Event Counts")
    ax1_s.set_xlabel("")
    ax1_s.legend()

    ax2_s.set_xlabel(column)

    fig_s.tight_layout()
    fig_s.savefig(f"test_new_signal_{column}.png")
    
