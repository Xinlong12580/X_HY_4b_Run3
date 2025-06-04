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
MC_weight = "genWeight"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_selection_TH.pkl" 
root_save_name = "All_selection.root" 



#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
h_data = {}
for year in years:
    h_data[year] = {}
    for column in bins:
        h_data[year][column] = ROOT.TH1D(f"selection_{year}_Data_Data_{column}_1", f"selection_{year}_Data_Data_{column}_1", len(bins[column]) - 1, bins[column])

for template_file in template_files:
    if "JetMET" in template_file:
        for year in years:
            if (year + "_") in template_file:
                print(template_file)
                f = ROOT.TFile.Open(template_file, "READ")
                for key in f.GetListOfKeys():
                    hist = key.ReadObj()
                    if isinstance(hist, ROOT.TH1):  
                        hist_name = hist.GetName()
                        print(hist_name)
                        for column in bins:
                            if column in hist_name:
                                h_data[year][column].Add(hist)
                f.Close()



print("Loading data successful")

#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling
h_BKGs = {}

for year in years:
    h_BKGs[year] = {}
    for process in processes:
        h_BKGs[year][process] = {}
        for subprocess in processes[process]:
            if subprocess == "*":
                if "SignalMC_" in process:
                    for _subprocess in signal_json[year][process]:
                        h_BKGs[year][process][_subprocess] = {}
                        for column in var_columns:
                            h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", len(bins[column]) - 1, bins[column])
                    break
                elif "MC_" in process:
                    for _subprocess in Xsec_json[process]:
                        h_BKGs[year][process][_subprocess] = {}
                        for column in var_columns:
                            h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", len(bins[column]) - 1, bins[column])
                    break
            else:
                h_BKGs[year][process][subprocess] = {}
                for column in var_columns:
                    h_BKGs[year][process][subprocess][column] = ROOT.TH1D(f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", f"selection_{year}_{process}_{subprocess}_{column}_{MC_weight}", len(bins[column]) - 1, bins[column])
            


BKG_fileWeight, BKG_totalWeight = load_weight(data_files, years, processes, signal_json, Xsec_json)







print("Loading BKG")


# making templates
for template_file in template_files:
    for year in h_BKGs:
        if (year + "_" ) in template_file:
            for process in h_BKGs[year]:
                if process in template_file:
                    for subprocess in h_BKGs[year][process]:
                        if subprocess in template_file:
                            print(template_file)
                            f = ROOT.TFile.Open(template_file, "READ")
                            for key in f.GetListOfKeys():
                                hist = key.ReadObj()
                                if isinstance(hist, ROOT.TH1):  
                                hist_name = hist.GetName()
                                print(hist_name)
                                for column in bins:
                                    if column in hist_name:
                                        h_BKGs[year][column].Add(hist.Scale(1/BKG_totalWeight[process][subprocess]))
                            f.Close()
h_All = {"data" : h_data, "BKGs" : h_BKGs}
with open(save_name, "wb") as f:
    pickle.dump(h_All, f)

f = ROOT.TFile.Open(root_save_name, "RECREATE")
f.cd()
for year in h_data:
    for column in h_data[year]:
        h_data[year][column].Write()

for year in h_BKGs:
    for process in h_BKGs[year]:
        for subprocess in h_BKGs[year][process]:
            for column in h_BKGs[year][process][subprocess]:
                h_BKGs[year][process][subprocess][column].Write()
f.Close()

print("LOADING BKG SUCCESSFUL")
exit()

