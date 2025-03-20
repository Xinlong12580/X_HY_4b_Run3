import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
mplhep.style.use("CMS")

with open("test_data.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection/" + line.strip()) for line in lines]

bins = np.linspace(0, 1000, 101)
bin_centers = 0.5 * (bins[:-1] + bins[1:])

with open("raw_nano/Xsections_background.json") as f:
    bkg_json = json.load(f)

h_data = Hist.new.Var(bins, name="data", label="Data").Double()
h_QCDs = {}
QCD_fileWeight = {}
QCD_idxs = {}
QCD_totalWeight = {}
for subprocess in bkg_json["MC_QCDJets"]:
    h_QCDs[subprocess] = Hist.new.Var(bins, name="QCD", label="QCD").Double()
    QCD_fileWeight[subprocess] = []
    QCD_idxs[subprocess] = 0
    QCD_totalWeight[subprocess] = 0

for data_file in data_files:
    if "MC_QCDJets" in data_file:
        for subprocess in h_QCDs:
            if subprocess in data_file:
                QCD_fileWeight[subprocess].append(ROOT.RDataFrame("Runs", data_file).Sum("genEventSumw").GetValue())
for subprocess in QCD_fileWeight:
    QCD_totalWeight[subprocess] = sum(QCD_fileWeight[subprocess])

for data_file in data_files:
    if "JetMET" in data_file:
        print(data_file)
        rdf_np = ROOT.RDataFrame("Events", data_file).AsNumpy(["leadingFatJetPt"])
        h_data.fill(rdf_np["leadingFatJetPt"])
    if "MC_QCDJets" in data_file:
        print(data_file)
        for subprocess in h_QCDs:
            if subprocess in data_file:
                rdf = ROOT.RDataFrame("Events", data_file)
                if "leadingFatJetPt" not in rdf.GetColumnNames():
                    print("Empty File")
                else:
                    rdf_np = rdf.AsNumpy(["leadingFatJetPt", "lumiXsecWeight"])
                    h_QCDs[subprocess].fill(QCD = rdf_np["leadingFatJetPt"], weight = (rdf_np["lumiXsecWeight"] * QCD_fileWeight[subprocess][QCD_idxs[subprocess]] / QCD_totalWeight[subprocess]) )
                
                QCD_idxs[subprocess] += 1

h_QCD = Hist.new.Var(bins, name="QCD", label="QCD").Double()
for subprocess in h_QCDs:
    h_QCD += h_QCDs[subprocess]

print("READING ROOT SUCCESSFUL")

data_binned = h_data.values()
data_binned_error = np.sqrt((h_data.variances()))  # sqrt(N)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

ax1.errorbar(bin_centers, data_binned, yerr=data_binned_error, fmt='o', color='black', label='Data')
mplhep.histplot(h_QCD, yerr=True, histtype="step", label="QCD", ax = ax1)
mplhep.cms.label("Preliminary", data=True, year=2022, ax=ax1)
ax1.set_yscale("log")
ax1.set_ylabel("Event Counts")
ax1.set_xlabel("Leading Fat Jet Pt")
ax1.legend()

# Ratio subplot
#ratio = data_counts / total_mc_counts
#ratio_errors = data_errors / total_mc_counts
#ax2.errorbar(bin_centers, ratio, yerr=ratio_errors, fmt='o', color='black')
#ax2.axhline(1.0, linestyle='--', color='gray')
#ax2.set_ylim(0.5, 1.5)
#ax2.set_ylabel("Data / MC")
#ax2.set_xlabel("Observable")

plt.tight_layout()
plt.savefig("test.png")
#plt.show()
