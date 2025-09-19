import ROOT
import os
import numpy as np
import array
import json
from XHY4b_Helper import * 
from argparse import ArgumentParser
import os

parser=ArgumentParser()

parser.add_argument('--mode', type=str, action='store', required=False)
parser.add_argument('--type', type=str, action='store', required=False)

parser.add_argument('--mx', type=str, action='store', required=False)
parser.add_argument('--my', type=str, action='store', required=False)
args = parser.parse_args()

with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
with open(f"outputList/output_division_{args.mode}.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines if "Templates" not in line and "log" not in line]
VB1_files = [data_file for data_file in data_files if "VB1" in data_file and "nom" in data_file ]
#for VB1_file in VB1_files:
#    print(VB1_file)
#exit()
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition(f"{args.mode}/")
    template_file = data_files_part[0] + data_files_part[1] + "Templates_" + data_files_part[2]
    template_files.append(template_file)
systs = ["JES__up", "JES__down", "JER__up", "JER__down", "PileUp_Corr_up", "PileUp_Corr_down", "nominal"]
if args.type == "signal":
    processes = {"SignalMC_XHY4b": [f"MX-{args.mx}_MY-{args.my}"]}

elif args.type == "bkg":
    processes = { "MC_TTBarJets": ["*"], "MC_WZJets": ["Wto2Q-3Jets_HT-200to400", "Wto2Q-3Jets_HT-400to600", "Wto2Q-3Jets_HT-600to800", "Wto2Q-3Jets_HT-800", "Zto2Q-4Jets_HT-200to400", "Zto2Q-4Jets_HT-400to600", "Zto2Q-4Jets_HT-600to800", "Zto2Q-4Jets_HT-800"]}
elif args.type == "all":
    processes = { "MC_TTBarJets": ["*"], "MC_WZJets": ["Wto2Q-3Jets_HT-200to400", "Wto2Q-3Jets_HT-400to600", "Wto2Q-3Jets_HT-600to800", "Wto2Q-3Jets_HT-800", "Zto2Q-4Jets_HT-200to400", "Zto2Q-4Jets_HT-400to600", "Zto2Q-4Jets_HT-600to800", "Zto2Q-4Jets_HT-800"], "SignalMC_XHY4b": [f"MX-{args.mx}_MY-{args.my}"]}
for process in processes:
    if processes[process] == ["*"]:
        processes[process] = []
        if "SignalMC" in process:
            for mass in signal_json["2022"]["SignalMC_XHY4b"]:
                processes[process].append(mass)
        elif "MC" in process:
            for subprocess in Xsec_json[process]:
                processes[process].append(subprocess) 
print(processes)
#exit()
#print(VB1_files) 
#processes = ["JetMET", "MC_TTBarJets", "MC_WZJets", "SignalMC_XHY4b" ]

regions = ["SR1", "SR2", "SB1", "SB2", "VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
regions = ["SR1", "SR2", "SB1", "SB2", "VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
years = ["2022", "2022EE", "2023", "2023BPix"]
MJY_bins = array.array("d", np.linspace(0, 5000, 501) )
MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
hist_base = ROOT.TH2D(f"MJJvsMJY", f"MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins)
hists = {}
for year in years:
    hists[year] = {}
    if args.type == "bkg" or args.type == "all":
        hists[year]["JetMET"] = {}
        for region in regions:
            hists[year]["JetMET"][region] = {}
            for syst in systs:
                if syst == "nominal":
                    hists[year]["JetMET"][region][syst] = hist_base.Clone(f"{year}__JetMET__{region}__{syst}")
                else:
                    hists[year]["JetMET"][region][syst] = hist_base.Clone(f"{year}__JetMET__{region}__Y{year}_{syst}")
    if "SignalMC_XHY4b" in processes:
        for subprocess in processes["SignalMC_XHY4b"]:
            hists[year][f"SignalMC_XHY4b_{subprocess}"] = {}        
            for region in regions:
                hists[year][f"SignalMC_XHY4b_{subprocess}"][region] = {}
                for syst in systs:
                    if syst == "nominal":
                        hists[year][f"SignalMC_XHY4b_{subprocess}"][region][syst] = hist_base.Clone(f"{year}__SignalMC_XHY4b_{subprocess}__{region}__{syst}")
                    else:
                        hists[year][f"SignalMC_XHY4b_{subprocess}"][region][syst] = hist_base.Clone(f"{year}__SignalMC_XHY4b_{subprocess}__{region}__Y{year}_{syst}")
        
    for process in processes:
        if "SignalMC" in process:
            continue
        hists[year][process] = {}        
        for region in regions:
            hists[year][process][region] = {}
            for syst in systs:
                if syst == "nominal":
                    hists[year][process][region][syst] = hist_base.Clone(f"{year}__{process}__{region}__{syst}")
                else:
                    hists[year][process][region][syst] = hist_base.Clone(f"{year}__{process}__{region}__Y{year}_{syst}")
#print(hists)
#print(VB1_files)
BKG_fileWeight, BKG_totalWeight = load_weight(VB1_files, years, processes, signal_json, Xsec_json)
print(BKG_totalWeight)
if args.type == "bkg" or args.type == "all":
    processes["JetMET"] = {}
for f_name in template_files:
    for year in years:
        if (year + "__") in f_name:
            for process in processes:
                if process in f_name:
                    good = 0
                    if "MC" in process:
                        for subprocess in processes[process]:
                            if subprocess in f_name:
                                good = 1
                                break
                    else:
                        good = 1
                    if good == 0:
                        continue
                    print(f_name)
                    for region in regions:
                        if region in f_name:
                            f = ROOT.TFile.Open(f_name, "READ")
                            for key in f.GetListOfKeys():
                                hist = key.ReadObj()
                                if isinstance(hist, ROOT.TH2):  
                                    hist_name = hist.GetName()
                                    print(hist_name) 
                                    loaded = 0
                                    for syst in systs:
                                        if hist_name.endswith(syst):
                                            print(f"{year}_{process}_{region}_{syst}")
                                            if "MC" in process:
                                                for subprocess in processes[process]:
                                                    
                                                    if subprocess  + "_" in f_name:
                                                        if "SignalMC" in process:
                                                            hist.Scale(1/1000 / BKG_totalWeight[year][process][subprocess])
                                                            hists[year][f"{process}_{subprocess}"][region][syst].Add(hist)
                                                            print("TEST") 
                                                        else:
                                                            hist.Scale(1/BKG_totalWeight[year][process][subprocess])
                                                            hists[year][process][region][syst].Add(hist)
                                                        loaded = 1
                                                        break
                                                    
                                            else:
                                                hists[year][process][region][syst].Add(hist)
                                                loaded = 1
                                    print(f"HIST LOADING STATUS:  {loaded}")
                            f.Close()

hists_allyears = {}
for process in hists[years[0]]:
    hists_allyears[process] = {}        
    for region in regions:
        hists_allyears[process][region] = {}
        for syst in systs:
            hists_allyears[process][region][syst] = hist_base.Clone(f"Allyears__{process}__{region}__{syst}")
            #hists_allyears[process][region][syst] = hist_base.Clone(f"Allyears_{process}_{region}_{syst}")
            for year in years:
                hists_allyears[process][region][syst].Add(hists[year][process][region][syst])




if args.type == "bkg":
    f = ROOT.TFile.Open(f"Templates/Templates_{args.mode}_bkg.root", "RECREATE")
elif args.type == "signal":
    f = ROOT.TFile.Open(f"Templates/Templates_{args.mode}_SignalMC_XHY4b_MX-{args.mx}_MY-{args.my}.root", "RECREATE")
if args.type == "all":
    f = ROOT.TFile.Open(f"Templates/Templates_{args.mode}_all.root", "RECREATE")
f.cd()

for year in years:
    for process in hists[year]:
        for region in regions:
            for syst in systs:
                hists[year][process][region][syst].Write()

for process in hists_allyears:
    for region in regions:
        for syst in systs:
            hists_allyears[process][region][syst].Write()

f.Close()


   


    
