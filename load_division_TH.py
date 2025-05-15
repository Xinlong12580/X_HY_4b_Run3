import numpy as np
import matplotlib.pyplot as plt
import mplhep
import ROOT
import array
import json
import pickle

#-----------------------------------loading files for the templates --------------------------------------------
with open("outputList/output_division.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_division/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = {"MC_QCDJets": ["QCD-4Jets_HT-400to600", "QCD-4Jets_HT-600to800", "QCD-4Jets_HT-800to1000", "QCD-4Jets_HT-1000to1200", "QCD-4Jets_HT-1200to1500", "QCD-4Jets_HT-1500to2000", "QCD-4Jets_HT-2000"], "MC_TTBarJets": ["TTto4Q", "TTtoLNu2Q", "TTto2L2Nu"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
regions = ["VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
MJY_bins = array.array("d", np.linspace(0, 2000, 201) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 401) )
 
h_BKG = {}
h_data = {}

MC_weight = "genWeight"
mplhep.style.use("CMS")

h_base = ROOT.TH2D("BaseMass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
save_name = "pkls/hists_division_TH.pkl"
#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
h_data = {}
for year in years:
    h_data[year] = {}
    for region in regions:
        h_data[year][region] = h_base.Clone(f"2DMass_data_{year}_{region}")

for data_file in data_files:
    if "JetMET" in data_file:
        for year in years:
            if (year + "__") in data_file:
                for region in regions:
                    if region in data_file:
                        print(data_file)
                        rdf = ROOT.RDataFrame("Events", data_file)
                        if rdf.Count().GetValue() < 1:
                            print("Empty File")
                        else:
                            th2 = rdf.Histo2D((f"Mass_{data_file}", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MJY", "MJJ")
                            h_data[year][region].Add(th2.GetValue())

print("Loading data successful")

#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling
h_BKGs = {}
BKG_fileWeight = {}
BKG_totalWeight = {}

for year in years:
    h_BKGs[year] = {}
    BKG_fileWeight[year] = {}
    BKG_totalWeight[year] = {}
    for process in processes:
        h_BKGs[year][process] = {}
        BKG_fileWeight[year][process] = {}
        BKG_totalWeight[year][process] = {}
        for subprocess in processes[process]:
            if subprocess == "*":
                if "SignalMC_" in process:
                    for _subprocess in signal_json[year][process]:
                        BKG_fileWeight[year][process][_subprocess] = {}
                        BKG_totalWeight[year][process][_subprocess] = {}
                        h_BKGs[year][process][_subprocess] = {}
                        for region in regions:
                            BKG_fileWeight[year][process][_subprocess][region] = []
                            BKG_totalWeight[year][process][_subprocess][region] = 0
                            h_BKGs[year][process][_subprocess][region] = h_base.Clone(f"2DMass_MC_{year}_{process}_{_subprocess}_{region}")
                    break
                elif "MC_" in process:
                    for _subprocess in Xsec_json[process]:
                        BKG_fileWeight[year][process][_subprocess] = {}
                        BKG_totalWeight[year][process][_subprocess] = {}
                        h_BKGs[year][process][_subprocess] = {}
                        for region in regions:
                            BKG_fileWeight[year][process][_subprocess][region] = []
                            BKG_totalWeight[year][process][_subprocess][region] = 0
                            h_BKGs[year][process][_subprocess][region] = h_base.Clone(f"2DMass_MC_{year}_{process}_{_subprocess}_{region}")
                    break
            else:
                BKG_fileWeight[year][process][subprocess] = {}
                BKG_totalWeight[year][process][subprocess] = {}
                h_BKGs[year][process][subprocess] = {}
                for region in regions:
                    BKG_fileWeight[year][process][subprocess][region] = []
                    BKG_totalWeight[year][process][subprocess][region] = 0
                    h_BKGs[year][process][subprocess][region] = h_base.Clone(f"2DMass_MC_{year}_{process}_{subprocess}_{region}")
            
print(BKG_totalWeight)
# loading weight info
print("Loading Weight")

for data_file in data_files:
    for year in BKG_fileWeight:
        if (year + "__" ) in data_file:
            for process in BKG_fileWeight[year]:
                if process in data_file:
                    for subprocess in BKG_fileWeight[year][process]:
                        if subprocess in data_file:
                            for region in BKG_fileWeight[year][process][subprocess]:
                                if region in data_file:
                                    print(data_file)
                                    rdf_np = ROOT.RDataFrame("Runs", data_file).AsNumpy(["genEventSumw"])
                                    BKG_fileWeight[year][process][subprocess][region].append(sum(rdf_np["genEventSumw"]))
for year in BKG_fileWeight:
    for process in BKG_fileWeight[year]:
        for subprocess in BKG_fileWeight[year][process]:
            for region in BKG_fileWeight[year][process][subprocess]:
                BKG_totalWeight[year][process][subprocess][region] = sum(BKG_fileWeight[year][process][subprocess][region])

print("Loading BKG")


# making templates
for data_file in data_files:
    for year in h_BKGs:
        lumi = lumi_json[year]
        if (year + "__" ) in data_file:
            for process in h_BKGs[year]:
                if process in data_file:
                    for subprocess in h_BKGs[year][process]:
                        if subprocess in data_file:
                            for region in regions:
                                if region in data_file:
                                    print(data_file)
                                    if "SignalMC_" in process:
                                        Xsec = 1
                                    elif "MC_" in process:
                                        Xsec = Xsec_json[process][subprocess]
                                    rdf = ROOT.RDataFrame("Events", data_file)
                                    if rdf.Count().GetValue() <= 0 or len(rdf.GetColumnNames()) < 1:
                                        print("Empty File")
                                    else:
                                        rdf = rdf.Define("NormalizedWeight", f"{lumi * Xsec / BKG_totalWeight[year][process][subprocess][region]} * {MC_weight}")
                                        th2 = rdf.Histo2D((f"Mass_{data_file}", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MJY", "MJJ", "NormalizedWeight")
                                        h_BKGs[year][process][subprocess][region].Add(th2.GetValue())
h_All = {"data" : h_data, "BKGs" : h_BKGs}
with open(save_name, "wb") as f:
    pickle.dump(h_All, f)

print("LOADING BKG SUCCESSFUL")
exit()
