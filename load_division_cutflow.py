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
with open("division_output.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_division/" + line.strip()) for line in lines]

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)


#----------------------------- set bins, variable columns and other configs--------------------------------------------------------------------
  
cuts = ["Region_VB1", "BeforeSkim", "Skim", "GoldenJson", "SkimOf1p1", "LeptonVeto", "TriggerCut", "FlagCut", "FatJetID", "FatJetPt", "FatJetMass", "DeltaEta", "MassJJ", "HiggsMatch"]
cutflows = {}
years = ["2022", "2022EE", "2023", "2023BPix"]
for cut in cuts:
    cutflows[cut] = {}
    for year in years:
        cutflows[cut][year] = {}
MC_weight = "genWeight"
mplhep.style.use("CMS")

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
#------------------------------ making data template ------------------------------------------------------------

print("Loading data")
for cut in cuts:
    for year in years:
        cutflows[cut][year]["data"] = 0

for data_file in data_files:
    if "VB1" not in data_file:
        continue
    if "JetMET" in data_file:
        for year in years:
            if (year + "__") in data_file:
                print(data_file)
                rdf = ROOT.RDataFrame("Cutflow", data_file)
                if rdf.Count().GetValue() < 1:
                    print("Empty File")
                else:
                    rdf_np = rdf.AsNumpy()
                    for cut in cuts:
                         cutflows[cut][year]["data"] += sum(rdf_np[cut])

print("Loading data successful")

#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling
BKG_fileWeight = {}
BKG_totalWeight = {}

for year in years:
    BKG_fileWeight[year] = {}
    BKG_totalWeight[year] = {}
    for process in processes:
        BKG_fileWeight[year][process] = {}
        BKG_totalWeight[year][process] = {}
        for subprocess in processes[process]:
            if subprocess == "*":
                if "SignalMC_" in process:
                    for _subprocess in signal_json[year][process]:
                        BKG_fileWeight[year][process][_subprocess] = []
                        BKG_totalWeight[year][process][_subprocess] = 0
                    break
                elif "MC_" in process:
                    for _subprocess in Xsec_json[process]:
                        BKG_fileWeight[year][process][_subprocess] = []
                        BKG_totalWeight[year][process][_subprocess] = 0
                    break
            else:
                BKG_fileWeight[year][process][subprocess] = []
                BKG_totalWeight[year][process][subprocess] = 0
for cut in cuts:            
    for year in years:
        for process in processes:
            cutflows[cut][year][process] = {}
            for subprocess in processes[process]:
                if subprocess == "*":
                    if "SignalMC_" in process:
                        for _subprocess in signal_json[year][process]:
                            cutflows[cut][year][process][_subprocess] = 0
                        break
                    elif "MC_" in process:
                        for _subprocess in Xsec_json[process]:
                            cutflows[cut][year][process][_subprocess] = 0
                        break
                else:
                    cutflows[cut][year][process][subprocess] = 0
print(BKG_totalWeight)
# loading weight info
print("Loading Weight")

for data_file in data_files:
    if "VB1" not in data_file:
        continue
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
    if "VB1" not in data_file:
        continue
    for year in cutflows["Skim"]:
        lumi = lumi_json[year]
        if (year + "__" ) in data_file:
            for process in cutflows["Skim"][year]:
                if process in data_file:
                    for subprocess in cutflows["Skim"][year][process]:
                        if subprocess in data_file:
                            print(data_file)
                            if "SignalMC_" in process:
                                Xsec = 1
                            elif "MC_" in process:
                                Xsec = Xsec_json[process][subprocess]
                            rdf = ROOT.RDataFrame("Cutflow", data_file )
                            if rdf.Count().GetValue() <= 0 or len(rdf.GetColumnNames()) < 1:
                                print("Empty File")
                            else:
                                rdf_np = rdf.AsNumpy()
                                for cut in cuts:
                                    if cut == "GoldenJson":
                                        cut_before = cuts[cuts.index(cut) - 1]
                                        cutflows[cut][year][process][subprocess] += sum(rdf_np[cut_before]) * (lumi * Xsec / BKG_totalWeight[year][process][subprocess])
                                    else:
                                        print(sum(rdf_np[cut]))
                                        cutflows[cut][year][process][subprocess] += sum(rdf_np[cut]) * (lumi * Xsec / BKG_totalWeight[year][process][subprocess])
        

with open("hists_selection_cutflow.pkl", "wb") as f:
    pickle.dump(cutflows, f)

print("LOADING BKG SUCCESSFUL")
exit()

