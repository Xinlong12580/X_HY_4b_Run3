import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Load data from file
data = np.loadtxt("matching_eff_withPNet.txt")
#data = np.loadtxt("Y_matching_eff.txt")

# Separate into columns
MX_vals = data[:, 0]
MY_vals = data[:, 1]
effs_vals = {"1p0": data[:, 2], "2p0": data[:, 3], "0p2": data[:, 4], "0p1": data[:, 5] , "1p1": data[:, 6], "2p1": data[:, 7], "1p2": data[:, 8], "2p2": data[:, 9],}

for mode in effs_vals:
    # Create scatter plot with colormap
    plt.figure(figsize=(10, 6))
    #sc = plt.scatter(MX_vals, MY_vals, c=effs_vals, cmap="viridis", s=100, edgecolors='k', vmin=0.0, vmax=0.3)
    #sc = plt.scatter(MX_vals, MY_vals, c=effs_vals, cmap="viridis", s=100, edgecolors='k', norm=LogNorm())
    sc = plt.scatter(MX_vals, MY_vals, c=effs_vals[mode], cmap="viridis", s=100, edgecolors='k')
    #sc = plt.scatter(MX_vals, MY_vals, c=effs_vals[mode], cmap="viridis", s=100, edgecolors='k', vmin=0.0, vmax=1)
    #sc = plt.scatter(MX_vals, MY_vals, c=effs_vals[mode], cmap="hot_r", s=100, edgecolors='k', vmin=0.0, vmax=1)

    # Add colorbar
    cbar = plt.colorbar(sc)
    cbar.set_label("Efficiency")

    # Axis labels and title
    plt.xlabel("MX")
    plt.ylabel("MY")
    plt.title(f"Y Matching Efficiency Map (MX vs. MY) with PNet, {mode}")
    #plt.title("Y Matching Efficiency Map (MX vs. MY)")
    plt.grid(True)
    #plt.yscale("log")
    plt.tight_layout()

    # Save plot
    plt.savefig(f"linear_{mode}_eff_map_withPNet.png", dpi=300)
    plt.xscale("log")
    plt.yscale("log")
    plt.savefig(f"log_{mode}_eff_map_withPNet.png", dpi=300)
    
    #plt.savefig("Y_eff_map.png", dpi=300)
