import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle

with open("hists_selection.pkl", "rb") as f:
    hists = pickle.load(f)
h_data = hists["data"]
h_BKGs = hists["BKGs"]
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
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}

#--------------------- extracting interested processes-----------------------------------------------
data_binned = {}
data_binned_error = {}
for year in years:
    data_binned[year] = {}
    data_binned_error[year] = {}
    for column in var_columns:
        data_binned[year][column] = h_data[year][column].values()
        data_binned_error[year][column] = np.sqrt((h_data[year][column].variances()))  # sqrt(N)

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
for year in years:
    h_QCD[year] = {}
    h_WZ[year] = {}
    h_Higgs[year] = {}
    h_TTBar[year] = {}
    h_Diboson[year] = {}
    h_SingleTop[year] = {}
    h_Signal[year] = {}
    h_All[year] = {}
    ratio[year] = {}
    ratio_error[year] = {}

    for column in var_columns:
        h_QCD[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_WZ[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_Higgs[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_TTBar[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_Diboson[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_SingleTop[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_Signal[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        h_All[year][column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
        ratio[year][column] = []
        ratio_error[year][column] = []
for year in years:
    for subprocess in h_BKGs[year]["MC_QCDJets"]:
        if subprocess == "QCD-4Jets_HT-100to200": #This one seems to be buggy, ignore it
            continue
        for column in var_columns:
            h_QCD[year][column] += h_BKGs[year]["MC_QCDJets"][subprocess][column]

    for subprocess in h_BKGs[year]["MC_WZJets"]:
        for column in var_columns:
            h_WZ[year][column] += h_BKGs[year]["MC_WZJets"][subprocess][column]

    for subprocess in h_BKGs[year]["MC_HiggsJets"]:
        #if subprocess == "WplusH_Hto2B_Wto2Q_M-125": #This one seems to be buggy, ignore it
        #    continue
        for column in var_columns:
            h_Higgs[year][column] += h_BKGs[year]["MC_HiggsJets"][subprocess][column]

    for subprocess in h_BKGs[year]["MC_TTBarJets"]:
        for column in var_columns:
            h_TTBar[year][column] += h_BKGs[year]["MC_TTBarJets"][subprocess][column]

    for subprocess in h_BKGs[year]["MC_DibosonJets"]:
        for column in var_columns:
            h_Diboson[year][column] += h_BKGs[year]["MC_DibosonJets"][subprocess][column]

    for subprocess in h_BKGs[year]["MC_SingleTopJets"]:
        for column in var_columns:
            h_SingleTop[year][column] += h_BKGs[year]["MC_SingleTopJets"][subprocess][column]

    for subprocess in h_BKGs[year]["SignalMC_XHY4b"]:
        for column in var_columns:
            h_Signal[year][column] += h_BKGs[year]["SignalMC_XHY4b"][subprocess][column]

    for column in var_columns:
        h_All[year][column] =  h_QCD[year][column] + h_WZ[year][column] + h_TTBar[year][column] + h_Higgs[year][column] + h_Diboson[year][column] + h_SingleTop[year][column]
        ratio[year][column] = [x / y for x,y in zip(data_binned[year][column], h_All[year][column].values())]
        ratio_error[year][column] = [x / y for x,y in zip(data_binned_error[year][column], h_All[year][column].values())]



#-------------------------------Ploting -----------------------------------------------------------

for year in years:
    for column in var_columns:

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        ax1.errorbar(bin_centers[column], data_binned[year][column], yerr=data_binned_error[year][column], fmt='o', color='black', label='Data')
        mplhep.histplot(
            [h_SingleTop[year][column], h_Diboson[year][column], h_Higgs[year][column], h_TTBar[year][column], h_WZ[year][column], h_QCD[year][column] ],
            label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            [h_SingleTop[year][column], h_Diboson[year][column], h_Higgs[year][column], h_TTBar[year][column], h_WZ[year][column], h_QCD[year][column] ],
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

        ax2.errorbar(bin_centers[column], ratio[year][column], yerr=ratio_error[year][column], fmt='o', color='black', label='Data')
        ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
        ax2.set_ylabel("Data/MC")
        ax2.set_ylim(0, 2)
        ax2.set_xlabel(column)

        fig.tight_layout()
        fig.savefig(f"plots_selection/stack_{year}_{column}.png")
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"plots_selection/linear_stack_{column}.png")

    
        #----plotting signal------

        fig_s, (ax1_s, ax2_s) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        mplhep.histplot(
            [h_Signal[year][column] ],
            label = ["Signal MX-3000_MY-300 (1 pb)"],
            color = ["purple"],
            stack = True,
            histtype = "fill",
            ax = ax1_s,
        )
        mplhep.histplot(
            [h_Signal[year][column] ],
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
        fig_s.savefig(f"plots_selection/signal_{year}_{column}.png")
        ax1_s.set_yscale("linear")
        ax1_s.set_ylim(auto = True)
        fig_s.savefig(f"plots_selection/linear_signal_{year}_{column}.png")
    
