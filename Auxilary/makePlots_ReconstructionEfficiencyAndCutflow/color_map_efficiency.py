import numpy as np
import matplotlib.pyplot as plt

mode = "2p1"
# Load data from file
data = np.loadtxt(f"{mode}_eff.txt")

# Separate into columns
MX_vals = data[:, 0]
MY_vals = data[:, 1]
eff_vals = data[:, 2]

# Create scatter plot with colormap
plt.figure(figsize=(10, 6))
#sc = plt.scatter(MX_vals, MY_vals, c=eff_vals, cmap="hot", s=100, edgecolors='k', vmin=0.0, vmax=0.08)
sc = plt.scatter(MX_vals, MY_vals, c=eff_vals, cmap="viridis", s=100, edgecolors='k')

# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label("Efficiency")

# Axis labels and title
plt.xlabel("MX")
plt.ylabel("MY")
plt.title("Efficiency Map (MX vs. MY) with gen matching(Loose)")
plt.grid(True)
plt.tight_layout()

# Save plot
plt.savefig(f"Loose_gen_eff_map_{mode}.png", dpi=300)
plt.yscale("log")
plt.xscale("log")
plt.savefig(f"Loose_gen_eff_map_{mode}_log.png", dpi=300)
