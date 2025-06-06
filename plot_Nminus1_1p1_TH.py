import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
with open("pkls/hists_Nminus1_1p1_TH.pkl", "rb") as f:
    hists = pickle.load(f)
with open("raw_nano/color_scheme.json", "r") as f:
    color_scheme = json.load(f)
h_data = hists["data"]
h_BKGs = hists["BKGs"]
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------

bins = {}
bins["PtCut__FatJet_pt_nom_0"] = array.array("d", np.linspace(0, 1000, 51))
bins["PtCut__FatJet_pt_nom_1"] = array.array("d", np.linspace(0, 1000, 51))
bins["MassCut__FatJet_msoftdrop_nom_0"] = array.array("d", np.linspace(0, 1000, 51))
bins["MassCut__FatJet_msoftdrop_nom_1"] = array.array("d", np.linspace(0, 1000, 51))
bins["DeltaEtaCut__AbsDeltaEta"] = array.array("d", np.linspace(-3, 3, 21))
bins["MJJCut__MassLeadingTwoFatJets"] = array.array("d", np.linspace(0, 3000, 151))
bins["HiggsCut__FatJet_msoftdrop_nom_0"] = array.array("d", np.linspace(0, 1000, 51))
bins["HiggsCut__FatJet_msoftdrop_nom_1"] = array.array("d", np.linspace(0, 1000, 51))
bins["BTaggingCut__PNet_0"] = array.array("d", np.linspace(0, 1, 11))
#bins["BTaggingCut__PNet_1"] = array.array("d", np.linspace(0, 11, 101))

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_dir = "plots/plots_Nminus1_1p1_TH"
#-------------------------------------rebinning -----------------------------------------
h_BKGs_rebinned = {}

for year in h_BKGs:
    h_BKGs_rebinned[year] = {}
    for process in h_BKGs[year]:
        h_BKGs_rebinned[year][process] = {}
        for subprocess in h_BKGs[year][process]:
            h_BKGs_rebinned[year][process][subprocess] = {}
            for column in h_BKGs[year][process][subprocess]:
                h_BKGs_rebinned[year][process][subprocess][column] = rebin_TH1(h_BKGs[year][process][subprocess][column], bins[column])
                if "Signal" in process:
                     h_BKGs_rebinned[year][process][subprocess][column].Scale(0.03)
h_BKGs_rebinned_merged = {}
for year in h_BKGs_rebinned:
    h_BKGs_rebinned_merged[year] = {}
    for process in h_BKGs_rebinned[year]:
        h_BKGs_rebinned_merged[year][process] = {}
        for column in  bins:
            h_BKGs_rebinned_merged[year][process][column] = h_BKGs_rebinned[year][process][next(iter(h_BKGs_rebinned[year][process]))][column].Clone("mergingSubprocess_MC_{year}_{process}_{column}")
            h_BKGs_rebinned_merged[year][process][column].Reset()
            print(process)
            for subprocess in h_BKGs_rebinned[year][process]:
                h_BKGs_rebinned_merged[year][process][column].Add(h_BKGs_rebinned[year][process][subprocess][column])
################################################################################################################################
#-----------------------------------------making 2D plots-------------------------
########################################################################################################################
#--------------------- extracting interested processes-----------------------------------------------



#-------------------------------Ploting -----------------------------------------------------------

for year in years:
    for column in bins:

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        hs = []
        labels = []
        colors = []
        for process in h_BKGs_rebinned_merged[year]:
            labels.append(process)
            hs.append(h_BKGs_rebinned_merged[year][process][column])
            colors.append(color_scheme[process])
        '''mplhep.histplot(
            [h_BKGs_rebinned_merged[year][column], h_BKGs_rebinned_merged[year][column], h_BKGs_rebinned_merged[year][column], h_BKGs_rebinned_merged[year][column], h_BKGs_rebinned_merged[year][column], h_BKGs_rebinned_merged[year][column] ],
            label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )'''
        mplhep.histplot(
            hs,
            label = labels,
            color =  colors,
            stack = False,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            yerr = False,
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        '''
        ax2.errorbar(bin_centers[column], ratio[year][column], yerr=ratio_error[year][column], fmt='o', color='black', label='Data')
        ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
        ax2.set_ylabel("Data/MC")
        ax2.set_ylim(0, 2)
        ax2.set_xlabel(column)
        '''
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_{year}_{column}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/stack_{year}_{column}.png")

        '''    
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
        ax1_s.set_ylabel("Event Counts")
        ax1_s.set_xlabel("")
        ax1_s.legend()

        ax2_s.set_xlabel(column)

        fig_s.tight_layout()
        ax1_s.set_yscale("linear")
        ax1_s.set_ylim(auto = True)
        fig_s.savefig(f"{save_dir}/linear_signal_{year}_{column}.png")
        ax1_s.set_yscale("log")
        ax1_s.set_ylim(1,10000000)
        fig_s.savefig(f"{save_dir}/signal_{year}_{column}.png")
        '''
