import numpy as np
import ROOT
import matplotlib.pyplot as plt
import mplhep
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
ROOT.gROOT.SetBatch(True)
with open("hists_division_TH.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = array.array("d", np.linspace(0, 1000, 41) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 101) )
h_base = ROOT.TH2D("Mass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
#--------------------------make data histogram-----------------------------------------------------------------------------------------------
h_data = hists["data"]
h_BKGs = hists["BKGs"]


h_data_all = {}
h_BKGs_all = {}
for region in h_data["2022"]:
    h_data_all[region] = h_base.Clone(f"2DMass_data_all_{region}")

for process in h_BKGs["2022"]:
    h_BKGs_all[process] = {}
    for subprocess in h_BKGs["2022"][process]:
        h_BKGs_all[process][subprocess] = {}
        for region in h_BKGs["2022"][process][subprocess]:
            h_BKGs_all[process][subprocess][region] = h_base.Clone(f"2DMass_MC_all_{process}_{subprocess}_{region}")

for year in h_data:
    for region in h_data[year]:
        print(f"{year}_{region}")
        h_data_all[region].Add(h_data[year][region])
        
for year in h_BKGs:
    for process in h_BKGs[year]:
        for subprocess in h_BKGs[year][process]:
            for region in h_BKGs[year][process][subprocess]:
                h_BKGs_all[process][subprocess][region].Add(h_BKGs[year][process][subprocess][region])

h_data_MJY = {}
h_TTBar_MJY = {}
h_netQCD_MJY = {}
for region in h_data_all:
    h_data_MJY[region] = h_data_all[region].ProjectionX(f"MJY_data_{region}")
    h_TTBar_MJY[region] = h_BKGs_all["MC_TTBarJets"]["TTto4Q"][region].ProjectionX(f"MJY_TTBar_{region}")
    h_netQCD_MJY[region] = h_data_MJY[region].Clone(f"MJY_netQCD_{region}")
    h_netQCD_MJY[region].Add(h_TTBar_MJY[region], -1)

h_data_VS4_VB2_MJY_ratio = h_data_MJY["VS4"].Clone("MJY_data_VS4overVB2")
h_data_VS4_VB2_MJY_ratio.Divide(h_data_MJY["VB2"])
h_netQCD_VS4_VB2_MJY_ratio = h_netQCD_MJY["VS4"].Clone("MJY_netQCD_VS4overVB2")
h_netQCD_VS4_VB2_MJY_ratio.Divide(h_netQCD_MJY["VB2"])
hists = [h_data_MJY["VS4"], h_data_MJY["VB2"], h_netQCD_MJY["VS4"], h_netQCD_MJY["VB2"], h_data_VS4_VB2_MJY_ratio, h_netQCD_VS4_VB2_MJY_ratio]
for h in hists:
    c = ROOT.TCanvas()
    #h_VS4_VB2_MJY_ratio.Draw("HIST")   
    h.Draw("HIST")   
    c.Update()
    c.SaveAs(f"{h.GetName()}.png")


