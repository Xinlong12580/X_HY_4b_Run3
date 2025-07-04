import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
print("TEST")
#-----------------------------------loading files for the templates --------------------------------------------
with open("outputList/output_selection.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines]
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "nom" in data_file)]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("nom")
    template_file = data_files_part[0] + "Templates_" + data_files_part[1] + data_files_part[2]
    template_files.append(template_file)
    
with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix"]
bins = {}
bin_centers = {}
bins["leadingFatJetPt"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtHiggsCandidate"] =array.array("d", np.linspace(0, 3000, 301) )
bins["PtYCandidate"] =array.array("d", np.linspace(0, 3000, 301) )

bins["leadingFatJetPhi"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiHiggsCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiYCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["leadingFatJetEta"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaHiggsCandidate"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaYCandidate"] = array.array("d", np.linspace(-3, 3, 21) )

bins["leadingFatJetMsoftdrop"] = array.array("d", np.linspace(0, 3000, 301) )
bins["MassLeadingTwoFatJets"] = array.array("d", np.linspace(0, 5000, 501) )
bins["MassHiggsCandidate"] = array.array("d", np.linspace(0, 3000, 301) )
bins["MassYCandidate"] = array.array("d", np.linspace(0, 3000, 301) )
for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
MC_weight = "weight_All__nominal"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_selection_1p1_TH.pkl" 
root_save_name = "All_selection.root" 


load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, signal_json)
