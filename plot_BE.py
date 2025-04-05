import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import json
import pickle

#-----------------------------------loading files for the templates --------------------------------------------
with open("selection_output.txt") as f:
    lines = f.readlines()
    selected_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection2/" + line.strip()) for line in lines]

with open("division_output.txt") as f:
    lines = f.readlines()
    divided_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_division/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
Processes = ["MC_QCDJets", "Data"]
QCD_subprocesses = ["QCD-4Jets_HT-400to600", "QCD-4Jets_HT-600to800", "QCD-4Jets_HT-800to1000", "QCD-4Jets_HT-1000to1200", "QCD-4Jets_HT-1200to1500", "QCD-4Jets_HT-1500to2000", "QCD-4Jets_HT-2000"]
Regions = ["VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
MJY_bins = np.linspace(0, 1000, 41) 
MJJ_bins = np.linspace(0, 4000, 101) 
hists = {}
for process in Processes:
    hists[process] = {}
    for region in Regions:
        hists[process][region] = (
            Hist.new
            .Var(MJY_bins, name="MJY", label="MJY")
            .Var(MJJ_bins, name="MJJ", label="MJJ")
            .Double()
        )

    
MC_weight = "genWeight"
mplhep.style.use("CMS")

year = "2022"
mass_points = ["MX-3000_MY-300"] 
#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
for data_file in divided_files:
    if "JetMET" in data_file:
        for region in Regions:
            if region in data_file:
                print(data_file)
                rdf = ROOT.RDataFrame("Events", data_file)
                if rdf.Count().GetValue() < 1:
                    print("Empty File")
                else:
                    rdf_np = rdf.AsNumpy(["MJY", "MJJ"])
                    hists["Data"][region].fill(MJY = rdf_np["MJY"], MJJ = rdf_np["MJJ"])
print("Loading data successful")

#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling
QCD_fileWeight = {}
QCD_idxs = {}
QCD_totalWeight = {}

for subprocess in QCD_subprocesses:
    QCD_fileWeight[subprocess] = {}
    QCD_idxs[subprocess] = {}
    QCD_totalWeight[subprocess] = {}
    for region in Regions:
        QCD_fileWeight[subprocess][region] = []
        QCD_idxs[subprocess][region] = 0
        QCD_totalWeight[subprocess][region] = 0
            
# loading weight info
print("Loading Weight")

for data_file in divided_files:
    for subprocess in QCD_fileWeight:
        if subprocess in data_file:
            for region in QCD_fileWeight[subprocess]:
                if region in data_file:
                    print(data_file)
                    rdf_np = ROOT.RDataFrame("Runs", data_file).AsNumpy(["genEventSumw"])
                    QCD_fileWeight[subprocess][region].append(sum(rdf_np["genEventSumw"]))
for subprocess in QCD_fileWeight:
    for region in QCD_fileWeight[subprocess]:
        QCD_totalWeight[subprocess][region] = sum(QCD_fileWeight[subprocess][region])

print("Loading QCD")

lumi = lumi_json[year]

# making templates
for data_file in divided_files:
    for subprocess in QCD_fileWeight:
        if subprocess in data_file:
            for region in QCD_fileWeight[subprocess]:
                if region in data_file:
                    print(data_file)
                    Xsec = Xsec_json["MC_QCDJets"][subprocess]
                    rdf = ROOT.RDataFrame("Events", data_file)
                    if rdf.Count().GetValue() < 1:
                        print("Empty File")
                    else:
                        rdf_np = rdf.AsNumpy(["MJY", "MJJ"] + [MC_weight])
                        hists["MC_QCDJets"][region].fill(MJY = rdf_np["MJY"], MJJ = rdf_np["MJJ"], weight = (rdf_np[MC_weight] * lumi * Xsec / QCD_totalWeight[subprocess][region]) )                

with open("QCD_BE.pkl", "wb") as f:
    pickle.dump(hists, f)

print("LOADING QCD SUCCESSFUL")

exit()
#--------------------- extracting interested processes-----------------------------------------------
h_QCD = {}
h_WZ = {}
h_Higgs = {}
h_TTBar = {}
h_Diboson = {}
h_SingleTop = {}
h_Signal = {}
h_All = {}
ratio = {}
ratio_error = {}
for column in var_columns:
    h_QCD[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_WZ[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Higgs[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_TTBar[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Diboson[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_SingleTop[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_Signal[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    h_All[column] = Hist.new.Var(bins[column], name="BKG", label="BKG").Double()
    ratio[column] = []
    ratio_error[column] = []
for subprocess in h_BKGs["MC_QCDJets"]:
    for column in var_columns:
        h_QCD[column] += h_BKGs["MC_QCDJets"][subprocess][column]

for subprocess in h_BKGs["MC_WZJets"]:
    for column in var_columns:
        h_WZ[column] += h_BKGs["MC_WZJets"][subprocess][column]



for subprocess in h_BKGs["MC_HiggsJets"]:
    for column in var_columns:
        h_Higgs[column] += h_BKGs["MC_HiggsJets"][subprocess][column]

for subprocess in h_BKGs["MC_TTBarJets"]:
    for column in var_columns:
        h_TTBar[column] += h_BKGs["MC_TTBarJets"][subprocess][column]

for subprocess in h_BKGs["MC_DibosonJets"]:
    for column in var_columns:
        h_Diboson[column] += h_BKGs["MC_DibosonJets"][subprocess][column]

for subprocess in h_BKGs["MC_SingleTopJets"]:
    for column in var_columns:
        h_SingleTop[column] += h_BKGs["MC_SingleTopJets"][subprocess][column]

for subprocess in h_BKGs["SignalMC_XHY4b"]:
    for column in var_columns:
        h_Signal[column] += h_BKGs["SignalMC_XHY4b"][subprocess][column]

for column in var_columns:
    h_All[column] =  h_QCD[column] + h_WZ[column] + h_TTBar[column] + h_Higgs[column] + h_Diboson[column] + h_SingleTop[column]
    ratio[column] = [x / y for x,y in zip(data_binned[column], h_All[column].values())]
    ratio_error[column] = [x / y for x,y in zip(data_binned_error[column], h_All[column].values())]



#-------------------------------Ploting -----------------------------------------------------------

with open("raw_nano/CMS_style.json") as f:
    CMS_style = json.load(f)
colors = CMS_style["color"]
for column in var_columns:
    h_QCD[column].label = "QCD"
    h_WZ[column].label = "WZ"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax1.errorbar(bin_centers[column], data_binned[column], yerr=data_binned_error[column], fmt='o', color='black', label='Data')
    mplhep.histplot(
        [h_SingleTop[column], h_Diboson[column], h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
        color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
        stack = True,
        histtype = "fill",
        ax = ax1,
    )
    mplhep.histplot(
        [h_SingleTop[column], h_Diboson[column], h_Higgs[column], h_TTBar[column], h_WZ[column], h_QCD[column] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1,
        linewidth = 1.2,
    )
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
    ax1.set_yscale("log")
    ax1.set_ylim(1,10000000)
    ax1.set_ylabel("Event Counts")
    ax1.set_xlabel("")
    ax1.legend()

    ax2.errorbar(bin_centers[column], ratio[column], yerr=ratio_error[column], fmt='o', color='black', label='Data')
    ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
    ax2.set_ylabel("Data/MC")
    ax2.set_ylim(0, 2)
    ax2.set_xlabel(column)

    fig.tight_layout()
    fig.savefig(f"test_new_{column}.png")
    
    #----plotting signal------

    fig_s, (ax1_s, ax2_s) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    mplhep.histplot(
        [h_Signal[column] ],
        label = ["Signal MX-3000_MY-300"],
        color = ["purple"],
        stack = True,
        histtype = "fill",
        ax = ax1_s,
    )
    mplhep.histplot(
        [h_Signal[column] ],
        stack = True,  # Note: keep stack=True so contours align with total stacks
        histtype = "step",
        color = "black",
        ax = ax1_s,
        linewidth = 1.2,
    )
    
    mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1_s)
    ax1_s.set_yscale("log")
    ax1_s.set_ylim(1,10000000)
    ax1_s.set_ylabel("Event Counts")
    ax1_s.set_xlabel("")
    ax1_s.legend()

    ax2_s.set_xlabel(column)

    fig_s.tight_layout()
    fig_s.savefig(f"test_new_signal_{column}.png")
    
