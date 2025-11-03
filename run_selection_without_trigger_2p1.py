#Running selection for mode 2p1
import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from XHY4b_Analyzer import *
from argparse import ArgumentParser
import os

#Reading input args. We do a selection for each JME correction
parser=ArgumentParser()
parser.add_argument('-d', type=str, dest='dataset',action='store', required=True)
parser.add_argument('-y', type=str, dest='year',action='store', required=True)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=True)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=True)
parser.add_argument('-s', type=str, dest='JME_syst',action='store', required=True)
args = parser.parse_args()

#cpp modules from Matej
CompileCpp("cpp_modules/deltaRMatching.cc")
CompileCpp("cpp_modules/helperFunctions.cc")
CompileCpp("cpp_modules/massMatching.cc")

CompileCpp("cpp_modules/selection_functions.cc")

#Specifying columns to save
columns = [ "MY", "MX", "leadingFatJetPt","leadingFatJetPhi","leadingFatJetEta", "leadingFatJetMsoftdrop", "PtJY0", "PtJY1", "EtaJY0", "EtaJY1", "PhiJY0", "PhiJY1", "MassJY0", "MassJY1", "MassJJH", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "MJJH", "MJY", "PNet_H", "PNet_Y0", "PNet_Y1", "Pileup_nTrueInt", "weight.*", "HLT.*"]

#Running selection
ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.selection_without_trigger_2p1()

#Saving snapshot and cutflow
file_basename = os.path.basename(args.dataset).removesuffix(".txt")
ana.output = "Trigger_Study_2p1" +"_tagged_selected_2p1_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"], saveRunChain = True)
else:
    ana.snapshot(columns, saveRunChain = True)
ana.save_cutflowInfo()

exit()


#Making histograms for several columns
bins = {}
bins["PtJY0"] = array.array("d", np.linspace(0, 3000, 101))
bins["PtJY1"] =array.array("d", np.linspace(0, 3000, 101) )
bins["PtHiggsCandidate"] =array.array("d", np.linspace(0, 3000, 101) )

bins["PhiJY0"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiJY1"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiHiggsCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["EtaJY0"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaJY1"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaHiggsCandidate"] = array.array("d", np.linspace(-3, 3, 21) )

bins["MassJY0"] = array.array("d", np.linspace(0, 1500, 51) )
bins["MassJY1"] = array.array("d", np.linspace(0, 5000, 101) )
bins["MassHiggsCandidate"] = array.array("d", np.linspace(0, 1500, 51) )
bins["MassYCandidate"] = array.array("d", np.linspace(0, 1500, 51) )
bins["MassJJH"] = array.array("d", np.linspace(1000, 4000, 51) )
bins["MJJH"] = array.array("d", np.linspace(1000, 4000, 51) )
bins["MJY"] = array.array("d", np.linspace(0, 1500, 51) )

#Saving histograms to a "Templates_" root file 
f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH1(bins, ["weight_All__nominal"], f)
else:
    ana.make_TH1(bins, [], f)
f.Close()
