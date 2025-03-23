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



#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
var_columns = ["leadingFatJetPt", "leadingFatJetPhi", "leadingFatJetEta"]
bins = {}
bin_centers = {}
bins["leadingFatJetPt"] = np.linspace(0, 2000, 51)
bins["leadingFatJetPhi"] = np.linspace(-np.pi, np.pi , 21)
bins["leadingFatJetEta"] = np.linspace(-3, 3, 21)
for column in var_columns:
    bin_centers[column] = 0.5 * (bins[column][:-1] + bins[column][1:])
MC_weight = "lumiXsecWeight"
mplhep.style.use("CMS")

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"]}

with open("hist.pkl", "rb")  as f:
    h_data = pickle.load(f)
    h_BKGs = pickle.load(f)

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
    #mplhep.cms.lumitext(r"7.9804 $fb^{-1}$ 2022(13.6 TeV)", ax = ax1)
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(1,10000000)
    if "Pt" in column:
        ax1.set_ylabel(f"Events/{(bin_centers[column][1] - bin_centers[column][0]):.0f}GeV")
    else:
        ax1.set_ylabel(f"Events/{(bin_centers[column][1] - bin_centers[column][0]):.2f}")
    if "Pt" in column:
        ax1.set_xlabel(column + "[GeV]")
    else:
        ax1.set_xlabel(column)
    ax1.legend()

    ax2.errorbar(bin_centers[column], ratio[column], yerr=ratio_error[column], fmt='o', color='black', label='Data')
    ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
    ax2.set_ylabel("Data/MC")
    ax2.set_ylim(0, 2)
    # Ratio subplot
    #ratio = data_counts / total_mc_counts
    #ratio_errors = data_errors / total_mc_counts
    #ax2.errorbar(bin_centers, ratio, yerr=ratio_errors, fmt='o', color='black')
    #ax2.axhline(1.0, linestyle='--', color='gray')
    #ax2.set_ylim(0.5, 1.5)
    #ax2.set_ylabel("Data / MC")
    #ax2.set_xlabel("Observable")

    plt.tight_layout()
    plt.savefig(f"test_new_{column}.png")

