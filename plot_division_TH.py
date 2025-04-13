import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle

with open("hists_division_TH.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = array.array("d", np.linspace(0, 1000, 41) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 101) )
h_base = ROOT.TH2D("Mass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
#--------------------------make data histogram-----------------------------------------------------------------------------------------------
h_data = hists["data"]
h_BKGs = hists["BKGs"]

h_data_all = {}
h_netQCD_all = {}
for region in h_data["2022"]:
    print(region)
    h_data_all[region] = h_base.Clone(f"2DMass_data_all_{region}")
    h_netQCD_all[region] = h_base.Clone(f"2DMass_netQCD_all_{region}")

for year in h_data:
    for region in h_data[year]:
        nbins_x = h_data[year][region].GetNbinsX()
        nbins_y = h_data[year][region].GetNbinsY()

        x_edges = np.array([h_data[year][region].GetXaxis().GetBinLowEdge(i+1) for i in range(nbins_x)] + [h_data[year][region].GetXaxis().GetBinUpEdge(nbins_x)])
        y_edges = np.array([h_data[year][region].GetYaxis().GetBinLowEdge(i+1) for i in range(nbins_y)] + [h_data[year][region].GetYaxis().GetBinUpEdge(nbins_y)])

# Fill the 2D array of contents
        z_data = np.array([[h_data[year][region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_ttbar = np.array([[h_BKGs[year]["MC_TTBarJets"]["TTto4Q"][region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_netQCD = z_data - z_ttbar 
        
        fig_data, ax_data = plt.subplots(figsize=(8, 6))
        mesh_data = ax_data.pcolormesh(x_edges, y_edges, z_data, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_data)  # Optional CMS-style label
        cbar = fig_data.colorbar(mesh_data, ax=ax_data, label="Entries")
        ax_data.set_xlabel("MJY")
        ax_data.set_ylabel("MJJ")
        fig_data.tight_layout()
        fig_data.savefig(f"{year}__data__{region}.png")



        fig_ttbar, ax_ttbar = plt.subplots(figsize=(8, 6))
        mesh_ttbar = ax_ttbar.pcolormesh(x_edges, y_edges, z_ttbar, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_ttbar)  # Optional CMS-style label
        cbar = fig_ttbar.colorbar(mesh_ttbar, ax=ax_ttbar, label="Entries")
        ax_ttbar.set_xlabel("MJY")
        ax_ttbar.set_ylabel("MJJ")
        fig_ttbar.tight_layout()
        fig_ttbar.savefig(f"{year}__ttbar__{region}.png")



        fig_netQCD, ax_netQCD = plt.subplots(figsize=(8, 6))
        mesh_netQCD = ax_netQCD.pcolormesh(x_edges, y_edges, z_netQCD, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_netQCD)  # Optional CMS-style label
        cbar = fig_netQCD.colorbar(mesh_netQCD, ax=ax_netQCD, label="Entries")
        ax_netQCD.set_xlabel("MJY")
        ax_netQCD.set_ylabel("MJJ")
        fig_netQCD.tight_layout()
        fig_netQCD.savefig(f"{year}__netQCD__{region}.png")






        h_data_all[region].Add(h_data[year][region])
        h_netQCD = h_data[year][region].Clone(f"2DMass_netQCD_{year}_{region}" )
        h_netQCD.Add(h_BKGs[year]["MC_TTBarJets"]["TTto4Q"][region], -1)
        h_netQCD_all[region].Add(h_netQCD)

for region in h_data_all:
    print(region)
    nbins_x = h_data[year][region].GetNbinsX()
    nbins_y = h_data[year][region].GetNbinsY()

    x_edges = np.array([h_data_all[region].GetXaxis().GetBinLowEdge(i+1) for i in range(nbins_x)] + [h_data_all[region].GetXaxis().GetBinUpEdge(nbins_x)])
    y_edges = np.array([h_data_all[region].GetYaxis().GetBinLowEdge(i+1) for i in range(nbins_y)] + [h_data_all[region].GetYaxis().GetBinUpEdge(nbins_y)])

    z_data = np.array([[h_data_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_netQCD = np.array([[h_netQCD_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_edges, y_edges, z_data, cmap="viridis")
        
    mplhep.cms.text("Simulation", ax=ax)  # Optional CMS-style label
    cbar = fig.colorbar(mesh, ax=ax, label="Entries")

    ax.set_xlabel("MJY")
    ax.set_ylabel("MJJ")
    plt.tight_layout()
    plt.savefig(f"ALL__data__{region}.png")

    fig_netQCD, ax_netQCD = plt.subplots(figsize=(8, 6))
    mesh_netQCD = ax_netQCD.pcolormesh(x_edges, y_edges, z_netQCD, cmap="viridis")        
    mplhep.cms.text("Simulation", ax = ax_netQCD)  # Optional CMS-style label
    cbar = fig_netQCD.colorbar(mesh_netQCD, ax=ax_netQCD, label="Entries")
    ax_netQCD.set_xlabel("MJY")
    ax_netQCD.set_ylabel("MJJ")
    fig_netQCD.tight_layout()
    fig_netQCD.savefig(f"ALL__netQCD__{region}.png")



