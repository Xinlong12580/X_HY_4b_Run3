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
with open("outputList/output_Nminus1_1p1.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines]
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "nom" in data_file)]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("nom")
    template_file = data_files_part[0] + "Templates_Nminus1_" + data_files_part[1] + data_files_part[2]
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
bins["PtCut__FatJet_pt_nom_0"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtCut__FatJet_pt_nom_1"] = array.array("d", np.linspace(0, 3000, 301))
bins["MassCut__FatJet_msoftdrop_nom_0"] = array.array("d", np.linspace(0, 3000, 301))
bins["MassCut__FatJet_msoftdrop_nom_1"] = array.array("d", np.linspace(0, 3000, 301))
bins["DeltaEtaCut__AbsDeltaEta"] = array.array("d", np.linspace(-3, 3, 21))
bins["MJJCut__MassLeadingTwoFatJets"] = array.array("d", np.linspace(0, 3000, 301))
bins["HiggsCut__FatJet_msoftdrop_nom_0"] = array.array("d", np.linspace(0, 3000, 301))
bins["HiggsCut__FatJet_msoftdrop_nom_1"] = array.array("d", np.linspace(0, 3000, 301))
bins["BTaggingCut__PNet_0"] = array.array("d", np.linspace(0, 1, 101))
#bins["BTaggingCut__PNet_1"] = array.array("d", np.linspace(0, 1, 101))
MC_weight = "weight_All__nominal"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_Nminus1_1p1_TH.pkl" 
root_save_name = "All_Nminus1_1p1.root" 


load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, signal_json)
