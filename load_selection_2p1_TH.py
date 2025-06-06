import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
print("TEST")
#-----------------------------------loading files for the templates --------------------------------------------
with open("selection_2p1_output.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection2_2p1_hadded/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix"]
var_columns = ["PtJY0", "PtJY1", "EtaJY0", "EtaJY1", "PhiJY0", "PhiJY1", "MassJY0", "MassJY1", "MassJJH", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "MJJH", "MJY"]
bins = {}
bin_centers = {}
bins["PtJY0"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtJY1"] =array.array("d", np.linspace(0, 3000, 301) )
bins["PtHiggsCandidate"] =array.array("d", np.linspace(0, 3000, 301) )

bins["PhiJY0"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiJY1"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiHiggsCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["EtaJY0"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaJY1"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaHiggsCandidate"] = array.array("d", np.linspace(-3, 3, 21) )

bins["MassJY0"] = array.array("d", np.linspace(0, 2000, 201) )
bins["MassJY1"] = array.array("d", np.linspace(0, 5000, 501) )
bins["MassHiggsCandidate"] = array.array("d", np.linspace(0, 2000, 201) )
bins["MassYCandidate"] = array.array("d", np.linspace(0, 2000, 201) )
bins["MassJJH"] = array.array("d", np.linspace(0, 4000, 401) )
bins["MJJH"] = array.array("d", np.linspace(0, 4000, 401) )
bins["MJY"] = array.array("d", np.linspace(0, 2000, 201) )
for column in var_columns:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
MC_weight = "genWeight"
mplhep.style.use("CMS")

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
h_data = {}
for year in years:
    h_data[year] = {}
    for column in var_columns:
        h_data[year][column] = ROOT.TH1D(f"selection_data_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])

for data_file in data_files:
    if "JetMET" in data_file:
        for year in years:
            if (year + "__") in data_file:
                print(data_file)
                rdf = ROOT.RDataFrame("Events", data_file, var_columns)
                if rdf.Count().GetValue() < 1:
                    print("Empty File")
                else:
                    for column in var_columns:
                        
                        th1 = rdf.Histo1D((f"selection_data_{data_file}", f"{column}", len(bins[column]) - 1, bins[column]), column)
                        h_data[year][column].Add(th1.GetValue())


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
                        BKG_fileWeight[year][process][_subprocess] = []
                        BKG_totalWeight[year][process][_subprocess] = 0
                        h_BKGs[year][process][_subprocess] = {}
                        for column in var_columns:
                            h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_MC_{process}_{_subprocess}_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
                    break
                elif "MC_" in process:
                    for _subprocess in Xsec_json[process]:
                        BKG_fileWeight[year][process][_subprocess] = []
                        BKG_totalWeight[year][process][_subprocess] = 0
                        h_BKGs[year][process][_subprocess] = {}
                        for column in var_columns:
                            h_BKGs[year][process][_subprocess][column] = ROOT.TH1D(f"selection_MC_{process}_{_subprocess}_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
                    break
            else:
                BKG_fileWeight[year][process][subprocess] = []
                BKG_totalWeight[year][process][subprocess] = 0
                h_BKGs[year][process][subprocess] = {}
                for column in var_columns:
                    h_BKGs[year][process][subprocess][column] = ROOT.TH1D(f"selection_MC_{process}_{subprocess}_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
            
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
                            print(data_file)
                            rdf_np = ROOT.RDataFrame("Runs", data_file).AsNumpy(["genEventSumw"])
                            BKG_fileWeight[year][process][subprocess].append(sum(rdf_np["genEventSumw"]))
for year in BKG_fileWeight:
    for process in BKG_fileWeight[year]:
        for subprocess in BKG_fileWeight[year][process]:
            BKG_totalWeight[year][process][subprocess] = sum(BKG_fileWeight[year][process][subprocess])

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
                            print(data_file)
                            if "SignalMC_" in process:
                                Xsec = 1
                            elif "MC_" in process:
                                Xsec = Xsec_json[process][subprocess]
                            rdf = ROOT.RDataFrame("Events", data_file, var_columns + [MC_weight])
                            if rdf.Count().GetValue() <= 0 or len(rdf.GetColumnNames()) < 1:
                                print("Empty File")
                            else:
                                print(lumi, BKG_totalWeight[year][process][subprocess])
                        
                                rdf = rdf.Define("ScaledWeight_selection", f"{lumi * Xsec / BKG_totalWeight[year][process][subprocess]} * {MC_weight}")
                                for column in var_columns:
                                    th1 = rdf.Histo1D((f"selection_MC_{data_file}", f"{column}", len(bins[column]) - 1, bins[column]), column, "ScaledWeight_selection")
                                    h_BKGs[year][process][subprocess][column].Add(th1.GetValue())
                            del rdf

h_All = {"data" : h_data, "BKGs" : h_BKGs}
with open("hists_selection_2p1_TH.pkl", "wb") as f:
    pickle.dump(h_All, f)

print("LOADING BKG SUCCESSFUL")
exit()

