import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from XHY4b_Analyzer import *
from argparse import ArgumentParser
import os

parser=ArgumentParser()
parser.add_argument('-d', type=str, dest='dataset',action='store', required=True)
parser.add_argument('-y', type=str, dest='year',action='store', required=True)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=True)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=True)
parser.add_argument('-s', type=str, dest='JME_syst',action='store', required=True)
args = parser.parse_args()

#dataset="raw_nano/files/2023_SignalMC_XHY4b_NMSSM_XtoYHto4B_MX-900_MY-95_TuneCP5_13p6TeV_madgraph-pythia8_Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2_NANOAODSIM.txt"
CompileCpp("cpp_modules/deltaRMatching.cc")
CompileCpp("cpp_modules/helperFunctions.cc")
CompileCpp("cpp_modules/massMatching.cc")
CompileCpp("cpp_modules/Matching.cc")
columns = ["leadingFatJetPt","leadingFatJetPhi","leadingFatJetEta", "leadingFatJetMsoftdrop", "MassLeadingTwoFatJets", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "PtYCandidate", "EtaYCandidate", "PhiYCandidate", "MJJ", "MJY", "PNet_H", "PNet_Y", "weight.*",  "FatJet_pt_JER__up", "PileUp_Corr__nom", "PileUp_Corr__up", "PileUp_Corr__down", "Pileup_nTrueInt"]
file_basename = os.path.basename(args.dataset).removesuffix(".txt")


ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.selection_1p1(args.JME_syst)
ana.output = args.JME_syst + "_tagged_selected_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

ana.save_fileInfo()
ana.save_cutflowInfo()
if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"])
else:
    ana.snapshot(columns)

if args.JME_syst != "nom":
    exit()
bins = {}

bins["leadingFatJetPt"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtHiggsCandidate"] =array.array("d", np.linspace(0, 3000, 301) )
bins["PtYCandidate"] =array.array("d", np.linspace(0, 3000, 301) )

bins["leadingFatJetPhi"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiHiggsCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiYCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["leadingFatJetEta"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaHiggsCandidate"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaYCandidate"] = array.array("d", np.linspace(-3, 3, 21) )

bins["leadingFatJetMsoftdrop"] = array.array("d", np.linspace(0, 3000, 301) )
bins["MassLeadingTwoFatJets"] = array.array("d", np.linspace(0, 5000, 501) )
bins["MassHiggsCandidate"] = array.array("d", np.linspace(0, 3000, 301) )
bins["MassYCandidate"] = array.array("d", np.linspace(0, 3000, 301) )

f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH1(bins, ["weight_All__nominal"], f)
else:
    ana.make_TH1(bins, [], f)
f.Close()
