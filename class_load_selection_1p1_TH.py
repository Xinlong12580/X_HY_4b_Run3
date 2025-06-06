import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
def load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, signal_json):
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
                            for column in bins:
                                h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", len(bins[column]) - 1, bins[column])
                        break
                    elif "MC_" in process:
                        for _subprocess in Xsec_json[process]:
                            h_BKGs[year][process][_subprocess] = {}
                            for column in bins:
                                h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", f"selection_{year}_{process}_{_subprocess}_{column}_{MC_weight}", len(bins[column]) - 1, bins[column])
                        break
                else:
                    h_BKGs[year][process][subprocess] = {}
                    for column in bins:
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
                                    if MC_weight in hist_name:
                                        for column in bins:
                                            if column in hist_name:
                                                hist.Scale(1/BKG_totalWeight[process][subprocess])
                                                h_BKGs[year][process][subprocess][column].Add(hist)
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
    
