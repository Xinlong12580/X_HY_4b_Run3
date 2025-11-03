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
columns = ["MY", "MX", "leadingFatJetPt","leadingFatJetPhi","leadingFatJetEta", "leadingFatJetMsoftdrop", "MassLeadingTwoFatJets", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "PtYCandidate", "EtaYCandidate", "PhiYCandidate", "MJJ", "MJY", "PNet_H", "PNet_Y", "weight.*",  "FatJet_pt_JER__up", "PileUp_Corr__nom", "PileUp_Corr__up", "PileUp_Corr__down", "Pileup_nTrueInt", "HLT.*"]

#Running selection
ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.selection_without_trigger_1p1()

#Saving snapshot and cutflow
file_basename = os.path.basename(args.dataset).removesuffix(".txt")
ana.output = "Trigger_Study_1p1" + "_tagged_selected_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"], saveRunChain = True)
else:
    ana.snapshot(columns, saveRunChain = True)
ana.save_cutflowInfo()
exit()

#Making a bunch of hitograms
bins = [{"leadingFatJetPt":array.array("d", np.linspace(0, 3000, 301)), "MassLeadingTwoFatJets": array.array("d", np.linspace(0, 5000, 501) ) }]

#Saving the histograms to the "Templates" root file
f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH2(bins, ["weight_All__nominal"], f)
else:
    ana.make_TH2(bins, [], f)
f.Close()
