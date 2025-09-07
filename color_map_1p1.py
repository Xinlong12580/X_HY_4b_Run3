import numpy as np
import matplotlib.pyplot as plt

# Load data from file
data = np.loadtxt("/uscms/home/rhmuifoo/nobackup/X_HY_4b_Run3/eff.txt")

# Separate into columns
MX_vals = data[:, 0]
MY_vals = data[:, 1]
eff_vals = data[:, 2]

# Create scatter plot with colormap
plt.figure(figsize=(10, 6))
sc = plt.scatter(MX_vals, MY_vals, c=eff_vals, cmap="hot", s=100, edgecolors='k', vmin=0.0, vmax=0.15)

# Add colorbar
cbar = plt.colorbar(sc)
cbar.set_label("Efficiency")

# Axis labels and title
plt.xlabel("MX")
plt.ylabel("MY")
plt.title("Efficiency Map (MX vs. MY)")
plt.grid(True)
plt.tight_layout()

# Save plot
plt.savefig("eff_map_1p1.pdf", dpi=300)


