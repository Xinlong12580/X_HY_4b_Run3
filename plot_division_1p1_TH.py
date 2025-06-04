import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
with open("pkls/hists_division_TH.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = array.array("d", np.linspace(0, 1000, 51) )
MJJ_bins = array.array("d", np.linspace(0, 3000, 101) )
MJY_bins = array.array("d", np.linspace(0, 2000, 101) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 401) )
h_base = ROOT.TH2D("Mass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
h_base_projx = h_base.ProjectionX("MassJY")
h_base_projy = h_base.ProjectionY("MassJJ")
nbins_x = len(MJY_bins) - 1
nbins_y = len(MJJ_bins) - 1

x_edges = np.array(MJY_bins)
y_edges = np.array(MJJ_bins)
h_data = hists["data"]
h_BKGs = hists["BKGs"]

#######################################################################################################################
#--------------------------rebinning  and creating projection hists--------------------------------------------------------------------------------
######################################################################################################################
h_data_rebinned = {}
h_data_rebinned_projx = {}
h_data_rebinned_projy = {}
h_BKGs_rebinned = {}
h_BKGs_rebinned_projx = {}
h_BKGs_rebinned_projy = {}
for year in h_data:
    h_data_rebinned[year] = {}
    h_data_rebinned_projx[year] = {}
    h_data_rebinned_projy[year] = {}
    for region in h_data[year]:
        h_data_rebinned[year][region] = rebin_TH2(h_data[year][region], MJY_bins, MJJ_bins)
        #h_data_rebinned[year][region] = h_data[year][region]
        h_data_rebinned_projx[year][region] = h_data_rebinned[year][region].ProjectionX(f"projx_data_{year}_{region}")
        h_data_rebinned_projy[year][region] = h_data_rebinned[year][region].ProjectionY(f"projy_data_{year}_{region}")

for year in h_BKGs:
    h_BKGs_rebinned[year] = {}
    h_BKGs_rebinned_projx[year] = {}
    h_BKGs_rebinned_projy[year] = {}
    for process in h_BKGs[year]:
        h_BKGs_rebinned[year][process] = {}
        h_BKGs_rebinned_projx[year][process] = {}
        h_BKGs_rebinned_projy[year][process] = {}
        for subprocess in h_BKGs[year][process]:
            h_BKGs_rebinned[year][process][subprocess] = {}
            h_BKGs_rebinned_projx[year][process][subprocess] = {}
            h_BKGs_rebinned_projy[year][process][subprocess] = {}
            for region in h_BKGs[year][process][subprocess]:
                h_BKGs_rebinned[year][process][subprocess][region] = rebin_TH2(h_BKGs[year][process][subprocess][region], MJY_bins, MJJ_bins)
                #h_BKGs_rebinned[year][process][subprocess][region] = h_BKGs[year][process][subprocess][region]
                h_BKGs_rebinned_projx[year][process][subprocess][region] = h_BKGs_rebinned[year][process][subprocess][region].ProjectionX(f"projx_MC_{year}_{process}_{subprocess}_{region}")
                h_BKGs_rebinned_projy[year][process][subprocess][region] = h_BKGs_rebinned[year][process][subprocess][region].ProjectionY(f"projy_MC_{year}_{process}_{subprocess}_{region}") 


############################################################################################################################
#--------------------------merging subprocesses------------------------------------------------------------------------------
#####################################################################################################################


h_BKGs_rebinned_merged = {}
h_BKGs_rebinned_projx_merged = {}
h_BKGs_rebinned_projy_merged = {}
for year in h_BKGs_rebinned:
    h_BKGs_rebinned_merged[year] = {}
    h_BKGs_rebinned_projx_merged[year] = {}
    h_BKGs_rebinned_projy_merged[year] = {}
    for process in h_BKGs_rebinned[year]:
        h_BKGs_rebinned_merged[year][process] = {}
        h_BKGs_rebinned_projx_merged[year][process] = {}
        h_BKGs_rebinned_projy_merged[year][process] = {}
        for region in h_data[year]:
            h_BKGs_rebinned_merged[year][process][region] = h_base.Clone("mergingSubprocess_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projx_merged[year][process][region] = h_base_projx.Clone("mergingSubprocess_projx_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projy_merged[year][process][region] = h_base_projy.Clone("mergingSubprocess_projy_MC_{year}_{process}_{region}")
            print(process)
            for subprocess in h_BKGs_rebinned[year][process]:
                h_BKGs_rebinned_merged[year][process][region].Add(h_BKGs_rebinned[year][process][subprocess][region])
                h_BKGs_rebinned_projx_merged[year][process][region].Add(h_BKGs_rebinned_projx[year][process][subprocess][region])
                h_BKGs_rebinned_projy_merged[year][process][region].Add(h_BKGs_rebinned_projy[year][process][subprocess][region])
################################################################################################################################
#-----------------------------------------making 2D plots-------------------------
########################################################################################################################
data_binned_projx = {}
data_binned_error_projx = {}
data_binned_projy = {}
data_binned_error_projy = {}
for year in h_data:
    data_binned_projx[year] = {}
    data_binned_error_projx[year] = {}
    data_binned_projy[year] = {}
    data_binned_error_projy[year] = {}
    for region in h_data[year]:
        data_binned_projx[year][region] = [h_data_rebinned_projx[year][region].GetBinContent(i) for i in range(1, h_data_rebinned_projx[year][region].GetNbinsX() + 1)]
        data_binned_error_projx[year][region] = [h_data_rebinned_projx[year][region].GetBinError(i) for i in range(1, h_data_rebinned_projx[year][region].GetNbinsX() + 1)]
        data_binned_projy[year][region] = [h_data_rebinned_projy[year][region].GetBinContent(i) for i in range(1, h_data_rebinned_projy[year][region].GetNbinsX() + 1)]
        data_binned_error_projy[year][region] = [h_data_rebinned_projy[year][region].GetBinError(i) for i in range(1, h_data_rebinned_projy[year][region].GetNbinsX() + 1)]



h_data_rebinned_all = {}
h_ttbar_rebinned_merged_all = {}
h_netQCD_rebinned_merged_all = {}
h_MCQCD_rebinned_merged_all = {}
for region in h_data["2022"]:
    print(region)
    h_data_rebinned_all[region] = h_base.Clone(f"2DMass_data_all_{region}")
    h_ttbar_rebinned_merged_all[region] = h_base.Clone(f"2DMass_ttbar_all_{region}")
    h_netQCD_rebinned_merged_all[region] = h_base.Clone(f"2DMass_netQCD_all_{region}")
    h_MCQCD_rebinned_merged_all[region] = h_base.Clone(f"2DMass_netQCD_all_{region}")

for year in h_data:
    for region in h_data[year]:
 
        h_data_rebinned_all[region].Add(h_data_rebinned[year][region])
        h_ttbar_rebinned_merged_all[region].Add(h_BKGs_rebinned_merged[year]["MC_TTBarJets"][region])
        h_netQCD = h_data_rebinned[year][region].Clone(f"2DMass_netQCD_{year}_{region}" )
        h_netQCD.Add(h_BKGs_rebinned_merged[year]["MC_TTBarJets"][region], -1)
        h_netQCD_rebinned_merged_all[region].Add(h_netQCD)
        h_MCQCD_rebinned_merged_all[region].Add(h_BKGs_rebinned_merged[year]["MC_QCDJets"][region])


        z_data = np.array([[h_data_rebinned[year][region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_ttbar = np.array([[h_BKGs_rebinned_merged[year]["MC_TTBarJets"][region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_MCQCD = np.array([[h_BKGs_rebinned_merged[year]["MC_QCDJets"][region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_netQCD = z_data - z_ttbar 
        
        zs = [z_data, z_ttbar, z_MCQCD, z_netQCD]
        processes = ["data", "ttbar", "MCQCD", "netQCD"] 
        for i in range(len(zs)):
            z = zs[i]
            process = processes[i]
            fig, ax = plt.subplots(figsize=(8, 6))
            mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis")        
            mplhep.cms.text("Simulation WiP", ax = ax)  # Optional CMS-style label
            cbar = fig.colorbar(mesh, ax=ax, label="Entries")
            ax.set_xlabel("MJY")
            ax.set_ylabel("MJJ")
            ax.set_title(f"{year} {process} {region}")
            fig.tight_layout()
            fig.savefig(f"plots/plots_division/{year}__{process}__{region}.png")



for region in h_data_rebinned_all:
    print(region)


    z_data = np.array([[h_data_rebinned_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_ttbar = np.array([[h_ttbar_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_netQCD = np.array([[h_netQCD_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_MCQCD = np.array([[h_MCQCD_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        
    zs = [z_data, z_ttbar, z_MCQCD, z_netQCD]
    processes = ["data", "ttbar", "MCQCD", "netQCD"] 
    for i in range(len(zs)):
        z = zs[i]
        process =   processes[i]
        fig, ax = plt.subplots(figsize=(8, 6))
        mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis") 
        mplhep.cms.text("Simulation WiP", ax=ax)  # Optional CMS-style label
        cbar = fig.colorbar(mesh, ax=ax, label="Entries")
        ax.set_xlabel("MJY")
        ax.set_ylabel("MJJ")
        ax.set_title(f"ALL__{process}__{region}")
        fig.tight_layout()
        fig.savefig(f"plots/plots_division/ALL__{process}__{region}.png")


#########################################################################################################################################
#----------------------------------------making stack plots ------------------------------------------------------------------------------------
##############################################################################################################################
for year in h_data:
    for region in h_data[year]:

        bin_centers_projx = (np.array(MJY_bins)[:-1] + np.array(MJY_bins)[1:])/2
        bin_centers_projy = (np.array(MJJ_bins)[:-1] + np.array(MJJ_bins)[1:])/2
        

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        ax1.errorbar(bin_centers_projx, data_binned_projx[year][region], yerr=data_binned_error_projx[year][region], fmt='o', color='black', label='Data')
        mplhep.histplot(
            #[h_BKGs_rebinned_projx_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_QCDJets"][region]],
            #label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            #color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            [h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_QCDJets"][region]],
            label = ["TTBar", "QCD"],
            color = ["lightblue", "orange"],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            #[h_BKGs_rebinned_projx_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_QCDJets"][region]],
            [h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"][region],  h_BKGs_rebinned_projx_merged[year]["MC_QCDJets"][region]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"plots/plots_division/linear_stack_projx_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"plots/plots_division/stack_projx_{year}_{region}.png")

    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        ax1.errorbar(bin_centers_projy, data_binned_projy[year][region], yerr=data_binned_error_projy[year][region], fmt='o', color='black', label='Data')
        mplhep.histplot(
            #[h_BKGs_rebinned_projy_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_QCDJets"][region]],
            #label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            #color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            [h_BKGs_rebinned_projy_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_QCDJets"][region]],
            label = [ "TTBar",  "QCD"],
            color = [ "lightblue",  "orange"],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            #[h_BKGs_rebinned_projy_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_QCDJets"][region]],
            [h_BKGs_rebinned_projy_merged[year]["MC_TTBarJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_QCDJets"][region]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"plots/plots_division/linear_stack_projy_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"plots/plots_division/stack_projy_{year}_{region}.png")
exit()         
##########################################################################################################################
#--------------------------------------fitting R_p/f------------------------------------------------------------------------
###################################################################################################################
h_netQCD_VS4_MJY_all = h_base_projx.Clone("h_netQCD_VS4_MJY_all")
h_netQCD_VB2_MJY_all = h_base_projx.Clone("h_netQCD_VB2_MJY_all")
for year in years:
    h_netQCD_VS4_MJY =  h_data_rebinned_projx[year]["VS4"].Clone(f"h_netQCD_VS4_MJY_{year}") 
    h_netQCD_VS4_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VS4"], -1)
    h_netQCD_VB2_MJY =  h_data_rebinned_projx[year]["VB2"].Clone(f"h_netQCD_VB2_MJY_{year}") 
    h_netQCD_VB2_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VB2"], -1)
    h_netQCD_VS4_MJY_all.Add(h_netQCD_VS4_MJY)
    h_netQCD_VB2_MJY_all.Add(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2 = h_netQCD_VS4_MJY.Clone(f"h_ratio_VS4_VB2_{year}")
    h_ratio_VS4_VB2.Devide(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2.GetName())
    c = ROOT.TCanvas()
    fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
    fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
    h_ratio_VS4_VB2.Draw("E")   
    fit_func.SetLineColor(ROOT.kRed)
    fit_func.Draw("SAME")
    c.Update()
    c.SaveAs(f"plots/VS4_VB2_fit/fitted_{year}_{h.GetName()}.png")

h_ratio_VS4_VB2 = h_netQCD_VS4_MJY_all.Clone("h_ratio_VS4_VB2_all")
h_ratio_VS4_VB2.Devide(h_netQCD_VB2_MJY_all)
h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2_all.GetName())
c = ROOT.TCanvas()
fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
h_ratio_VS4_VB2.Draw("E")
fit_func.SetLineColor(ROOT.kRed)
fit_func.Draw("SAME")
c.Update()
c.SaveAs(f"plots/VS4_VB2_fit/fitted_all_{h.GetName()}.png")
