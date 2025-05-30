import ROOT
import os
import numpy as np
import array
files = os.listdir("Templates")
files = ["Templates/" + f_name for f_name in files]
systs = ["JES__up", "JES__down", "JER__up", "JER__down", "PileUp_Corr_up", "PileUp_Corr_down", "nominal"]

processes = ["JetMET", "MC_TTBarJets", "MC_WZJets", "SignalMC_XHY4b" ]

regions = ["VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
years = ["2022", "2022EE", "2023", "2023BPix"]
MJY_bins = array.array("d", np.linspace(0, 2000, 201) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 401) )
hist_base = ROOT.TH2D(f"MJJvsMJY", f"MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins)
hists = {}
for year in years:
    hists[year] = {}
    for process in processes:
        hists[year][process] = {}        
        for region in regions:
            hists[year][process][region] = {}
            for syst in systs:
                hists[year][process][region][syst] = hist_base.Clone(f"{year}_{process}_{region}_{syst}")


for f_name in files:
    for year in years:
        if (year + "_") in f_name:
            print(f_name)
            for process in processes:
                if process in f_name:
                    f = ROOT.TFile.Open(f_name, "READ")
                    for key in f.GetListOfKeys():
                        hist = key.ReadObj()
                        if isinstance(hist, ROOT.TH2):  
                            hist_name = hist.GetName()
                            print(hist_name)
                            
                            for region in regions:
                                if region in hist_name:
                                    for syst in systs:
                                        if hist_name.endswith(syst):
                                            print(f"{year}_{process}_{region}_{syst}")
                                            hists[year][process][region][syst].Add(hist)
                                            print(hist.GetEntries())
                    f.Close()
hists_allyears = {}
for process in processes:
    hists_allyears[process] = {}        
    for region in regions:
        hists_allyears[process][region] = {}
        for syst in systs:
            hists_allyears[process][region][syst] = hist_base.Clone(f"Allyears_{process}_{region}_{syst}")
            for year in years:
                hists_allyears[process][region][syst].Add(hists[year][process][region][syst])





f = ROOT.TFile.Open("Templates_all.root", "RECREATE")
f.cd()

for year in years:
    for process in processes:
        for region in regions:
            for syst in systs:
                hists[year][process][region][syst].Write()

for process in processes:
    for region in regions:
        for syst in systs:
            hists_allyears[process][region][syst].Write()

f.Close()


   


    
''' 
for year in years:
    for process in processes:
        for syst in systs 
'''
