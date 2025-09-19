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
args = parser.parse_args()

#dataset="raw_nano/files/2023_SignalMC_XHY4b_NMSSM_XtoYHto4B_MX-900_MY-95_TuneCP5_13p6TeV_madgraph-pythia8_Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2_NANOAODSIM.txt"
CompileCpp("cpp_modules/deltaRMatching.cc")
CompileCpp("cpp_modules/helperFunctions.cc")
CompileCpp("cpp_modules/massMatching.cc")
CompileCpp("cpp_modules/selection_functions.cc")
columns = [ "PtJY0", "PtJY1", "EtaJY0", "EtaJY1", "PhiJY0", "PhiJY1", "MassJY0", "MassJY1", "MassJJH", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "MJJH", "MJY", "PNet_H", "PNet_Y0", "PNet_Y1", "Pileup_nTrueInt", "weight.*"]
file_basename = os.path.basename(args.dataset).removesuffix(".txt")


ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.analyzer.Cut("MJYCut", "MJY > 200")
ana.register_weight("MJYCut")
ana.output = "masscut_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"], saveRunChain = True)
else:
    ana.snapshot(columns, saveRunChain = True)
ana.save_cutflowInfo()

