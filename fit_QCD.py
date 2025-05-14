import numpy as np
import ROOT
import matplotlib.pyplot as plt
print("TEST")
import mplhep
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
ROOT.gROOT.SetBatch(True)
with open("hists_division_TH.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = array.array("d", np.array([ 60, 100, 140, 200, 300, 500]) )
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
    if "2023BPix" != year :
        continue
    print(year)
    for region in h_data[year]:
        print(f"{year}_{region}")
        h_data_all[region].Add(h_data[year][region])
        
for year in h_BKGs:
    if "2023BPix" != year:
        continue
    print(year)
    for process in h_BKGs[year]:
        for subprocess in h_BKGs[year][process]:
            for region in h_BKGs[year][process][subprocess]:
                h_BKGs_all[process][subprocess][region].Add(h_BKGs[year][process][subprocess][region])

h_data_MJY = {}
h_TTBar_MJY = {}
h_netQCD_MJY = {}
h_QCD_MJY = {}
for region in h_data_all:
    h_data_MJY[region] = h_data_all[region].ProjectionX(f"MJY_data_{region}")
    h_TTBar_MJY[region] = h_base.ProjectionX(f"MJY_TTBar_{region}")
    for subprocess in h_BKGs_all["MC_TTBarJets"]:
        print(subprocess)
        h_TTBar_MJY[region].Add(h_BKGs_all["MC_TTBarJets"][subprocess][region].ProjectionX(f"tmp_{subprocess}_{region}"))
    h_TTBar_MJY[region] = h_BKGs_all["MC_TTBarJets"]["TTto4Q"][region].ProjectionX(f"MJY_TTBar_{region}")
    h_QCD_MJY[region] = h_base.ProjectionX(f"MJY_QCD_{region}")
    for subprocess in h_BKGs_all["MC_QCDJets"]:
        h_QCD_MJY[region].Add(h_BKGs_all["MC_QCDJets"][subprocess][region].ProjectionX(f"tmp_{subprocess}_{region}"))
    h_netQCD_MJY[region] = h_data_MJY[region].Clone(f"MJY_netQCD_{region}")
    h_netQCD_MJY[region].Add(h_TTBar_MJY[region], -1)



h_data_VS4_VB2_MJY_ratio = h_data_MJY["VS4"].Clone("MJY_data_VS4overVB2")
h_data_VS4_VB2_MJY_ratio.Divide(h_data_MJY["VB2"])
h_netQCD_VS4_VB2_MJY_ratio = h_netQCD_MJY["VS4"].Clone("MJY_netQCD_VS4overVB2")
h_netQCD_VS4_VB2_MJY_ratio.Divide(h_netQCD_MJY["VB2"])

h_data_VS2_VB1_MJY_ratio = h_data_MJY["VS2"].Clone("MJY_data_VS2overVB1")
h_data_VS2_VB1_MJY_ratio.Divide(h_data_MJY["VB1"])
h_netQCD_VS2_VB1_MJY_ratio = h_netQCD_MJY["VS2"].Clone("MJY_netQCD_VS2overVB1")
h_netQCD_VS2_VB1_MJY_ratio.Divide(h_netQCD_MJY["VB1"])
h_TTBar_VS2_VB1_MJY_ratio = h_TTBar_MJY["VS2"].Clone("MJY_TTBar_VS2overVB1")
h_TTBar_VS2_VB1_MJY_ratio.Divide(h_TTBar_MJY["VB1"])

hists = [h_data_MJY["VS4"], h_data_MJY["VB2"], h_netQCD_MJY["VS4"], h_netQCD_MJY["VB2"], h_data_VS4_VB2_MJY_ratio, h_netQCD_VS4_VB2_MJY_ratio]
for h in hists:
    h.SetTitle(h.GetName())
    c = ROOT.TCanvas()
    #h_VS4_VB2_MJY_ratio.Draw("HIST")   
    h.Draw("HIST")   
    c.Update()
    c.SaveAs(f"{h.GetName()}.png")
'''
for region in h_data_all:
    h_TTBar_MJY[region].Add(h_QCD_MJY[region])

    
    c = ROOT.TCanvas()
    h_data_MJY[region].SetLineColor(ROOT.kBlue)
    h_QCD_MJY[region].SetLineColor(ROOT.kRed)
    h_TTBar_MJY[region].SetLineColor(ROOT.kGreen)
    h_data_MJY[region].Draw("HIST")
    h_QCD_MJY[region].Draw("HIST SAME")
    h_TTBar_MJY[region].Draw("HIST SAME")
    legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9)
    legend.AddEntry(h_data_MJY[region], "Data", "l")
    legend.AddEntry(h_QCD_MJY[region], "QCD", "l")
    legend.AddEntry(h_TTBar_MJY[region], "TTBar", "l")
    legend.Draw()
    c.Update()
    c.SaveAs(f"Compare_{region}.png")
'''

for region in h_data_all:
    data_binned = [h_data_MJY[region].GetBinContent(i) for i in range(1, h_data_MJY[region].GetNbinsX() + 1)]
    data_binned_error = [h_data_MJY[region].GetBinError(i) for i in range(1, h_data_MJY[region].GetNbinsX() + 1)]
    bin_centers = 0.5 * (np.array(MJY_bins)[:-1] + np.array(MJY_bins)[1:])
    print(data_binned)
    print(bin_centers)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax1.errorbar(bin_centers, data_binned, yerr=data_binned_error, fmt='o', color='black', label='Data')
    mplhep.histplot(
        [h_QCD_MJY[region], h_TTBar_MJY[region] ],
        label = ["QCD", "TTBar"],
        color = ["orange", "lightblue"],
        stack = True,
        histtype = "fill",
        ax = ax1,
    )
    mplhep.histplot(
        [h_QCD_MJY[region], h_TTBar_MJY[region] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1,
        linewidth = 1.2,
    )
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("linear")
    ax1.set_ylim(0, max(data_binned) * 2)
    ax1.set_ylabel("Event Counts")
    ax1.set_xlabel("")
    ax1.legend()


    fig.tight_layout()
    fig.savefig(f"COMPARE_{region}.png")

h = h_netQCD_VS4_VB2_MJY_ratio
h.SetTitle(h.GetName())
c = ROOT.TCanvas()
fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
fit_result = h.Fit(fit_func, "S")
h.Draw("E")   
fit_func.SetLineColor(ROOT.kRed)
fit_func.Draw("SAME")
c.Update()
c.SaveAs(f"fitted_{h.GetName()}.png")


Info_set = {"fitresult_VS4overVB2_MJY": fit_result, "fitfunc_VS4overVB2_MJY": fit_func, "h_data_VS2": h_data_all["VS2"], "h_data_VB1": h_data_all["VB1"], "h_ttbar_VS2": h_BKGs_all["MC_TTBarJets"]["TTto4Q"]["VS2"], "h_ttbar_VB1": h_BKGs_all["MC_TTBarJets"]["TTto4Q"]["VB1"]}

with open("Ratio_templates.pkl", "wb") as f:
    pickle.dump(Info_set, f)
