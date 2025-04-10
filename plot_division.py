import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle

with open("hists_division.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = np.linspace(0, 1000, 41) 
MJJ_bins = np.linspace(0, 4000, 101) 
h_base = (
    Hist.new
    .Var(MJY_bins, name="MJY", label="MJY")
    .Var(MJJ_bins, name="MJJ", label="MJJ")
    .Double()
) 
#--------------------------make data histogram-----------------------------------------------------------------------------------------------
h_data = hists["data"]
h_BKGs = hists["BKGs"]

h_data_all = {}
h_netQCD_all = {}
z_netQCD_all = {}
for region in h_data["2022"]:
    print(region)
    h_data_all[region] = h_base.copy()
    h_netQCD_all[region] = h_base.copy()
    z_netQCD_all[region] = np.zeros_like(h_data["2022"]["VB1"].values().T)

for year in h_data:
    for region in h_data[year]:
        x_edges = h_data[year][region].axes[0].edges
        y_edges = h_data[year][region].axes[1].edges
        z_data = h_data[year][region].values().T  # Transpose so x is horizontal, y is vertical
        z_ttbar = h_BKGs[year]["MC_TTBarJets"]["TTto4Q"][region].values().T
        z_netQCD = z_data - z_ttbar 
        
        fig_data, ax_data = plt.subplots(figsize=(8, 6))
        mesh_data = ax_data.pcolormesh(x_edges, y_edges, z_data, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_data)  # Optional CMS-style label
        cbar = fig_data.colorbar(mesh_data, ax=ax_data, label="Entries")
        ax_data.set_xlabel(h_data[year][region].axes[0].label)
        ax_data.set_ylabel(h_data[year][region].axes[1].label)
        fig_data.tight_layout()
        fig_data.savefig(f"{year}__data__{region}.png")



        fig_ttbar, ax_ttbar = plt.subplots(figsize=(8, 6))
        mesh_ttbar = ax_ttbar.pcolormesh(x_edges, y_edges, z_ttbar, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_ttbar)  # Optional CMS-style label
        cbar = fig_ttbar.colorbar(mesh_ttbar, ax=ax_ttbar, label="Entries")
        ax_ttbar.set_xlabel(h_data[year][region].axes[0].label)
        ax_ttbar.set_ylabel(h_data[year][region].axes[1].label)
        fig_ttbar.tight_layout()
        fig_ttbar.savefig(f"{year}__ttbar__{region}.png")



        fig_netQCD, ax_netQCD = plt.subplots(figsize=(8, 6))
        mesh_netQCD = ax_netQCD.pcolormesh(x_edges, y_edges, z_netQCD, cmap="viridis")        
        mplhep.cms.text("Simulation", ax = ax_netQCD)  # Optional CMS-style label
        cbar = fig_netQCD.colorbar(mesh_netQCD, ax=ax_netQCD, label="Entries")
        ax_netQCD.set_xlabel(h_data[year][region].axes[0].label)
        ax_netQCD.set_ylabel(h_data[year][region].axes[1].label)
        fig_netQCD.tight_layout()
        fig_netQCD.savefig(f"{year}__netQCD__{region}.png")






        h_data_all[region] += h_data[year][region]
        z_netQCD_all[region] += z_netQCD

for region in h_data_all:
    print(region)
    x_edges = h_data_all[region].axes[0].edges
    y_edges = h_data_all[region].axes[1].edges
    z = h_data_all[region].values().T  # Transpose so x is horizontal, y is vertical
        
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis")
        
    mplhep.cms.text("Simulation", ax=ax)  # Optional CMS-style label
    cbar = fig.colorbar(mesh, ax=ax, label="Entries")

    ax.set_xlabel(h_data_all[region].axes[0].label)
    ax.set_ylabel(h_data_all[region].axes[1].label)
    plt.tight_layout()
    plt.savefig(f"ALL__data__{region}.png")

for region in z_netQCD_all:
    print(region)
    x_edges = h_data_all[region].axes[0].edges
    y_edges = h_data_all[region].axes[1].edges
    z = z_netQCD_all[region]
        
    fig, ax = plt.subplots(figsize=(8, 6))
    mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis")
        
    mplhep.cms.text("Simulation", ax=ax)  # Optional CMS-style label
    cbar = fig.colorbar(mesh, ax=ax, label="Entries")

    ax.set_xlabel(h_data_all[region].axes[0].label)
    ax.set_ylabel(h_data_all[region].axes[1].label)
    plt.tight_layout()
    plt.savefig(f"ALL__netQCD__{region}.png")
exit()
