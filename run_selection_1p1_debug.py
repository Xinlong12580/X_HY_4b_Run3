# Running selection for mode 1p1
import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from XHY4b_Analyzer import *
from argparse import ArgumentParser
import os

#Reading input args
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
columns = ["leadingFatJetPt","leadingFatJetPhi","leadingFatJetEta", "leadingFatJetMsoftdrop", "MassLeadingTwoFatJets", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "PtYCandidate", "EtaYCandidate", "PhiYCandidate", "MJJ", "MJY", "PNet_H", "PNet_Y", "weight.*",  "FatJet_pt_JER__up", "PileUp_Corr__nom", "PileUp_Corr__up", "PileUp_Corr__down", "Pileup_nTrueInt"]

#Running selection
ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.selection_1p1_debug_v1(args.JME_syst)

#Saving snapshot and cutflow
file_basename = os.path.basename(args.dataset).removesuffix(".txt")
ana.output = args.JME_syst + "_tagged_selected_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"], saveRunChain = True)
else:
    ana.snapshot(columns, saveRunChain = True)
ana.save_cutflowInfo()

if args.JME_syst != "nom":
    exit()

#Making a bunch of hitograms
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

#Saving the histograms to the "Templates" root file
f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH1(bins, ["weight_All__nominal"], f)
else:
    ana.make_TH1(bins, [], f)
f.Close()
