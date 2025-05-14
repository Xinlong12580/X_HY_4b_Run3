import matplotlib.pyplot as plt

def plot_mass_points(file):
    Ms = []
    with open(file) as f:
        for line in f:
            MX_i_ind = line.find("_MX-") + 4
            MX_f_ind = line.find("_MY-")
            MY_i_ind = line.find("_MY-") + 4
            MY_f_ind = line.find("_Tune")
            MX = int(line[MX_i_ind : MX_f_ind])
            MY = int(line[MY_i_ind : MY_f_ind])
            #print(f"{MX} {MY}")
            Ms.append([MX, MY])
    return Ms

Ms2022 = plot_mass_points("signal_2022.txt")
Ms2022EE = plot_mass_points("signal_2022EE.txt")
Ms2023 = plot_mass_points("signal_2023.txt")
Ms2023BPix = plot_mass_points("signal_2023BPix.txt")

GoodMs = []
for M in Ms2022:
    if ((M in Ms2022EE) and (M in Ms2023) and (M in Ms2023BPix)):
        GoodMs.append(M)
print(len(GoodMs))
MXs = [row[0] for row in GoodMs]
MYs = [row[1] for row in GoodMs]

with open("GoodMassPoints.txt", "w") as f:
    for i in range(len(MXs)):
        f.write(f"{MXs[i]} {MYs[i]}\n")

        

fig = plt.figure(dpi=100, figsize = (10, 8))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(MXs, MYs, marker='*')
ax.set_xlim(100, 10000)
ax.set_ylim(50, 10000)
#ax.set_xticks([300, 3000])
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("MX(GeV)")
ax.set_ylabel("MY(GeV)")
plt.savefig("signal_mass_points.png")
