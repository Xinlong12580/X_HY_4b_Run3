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

CompileCpp("cpp_modules/skim_function.cc")
CompileCpp("cpp_modules/goldenJson_mask.cc")
#ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job, 10000)
ana.skim()
if "Data" in args.dataset:
    ana.mask_goldenJson()
    ana.cut_goldenJson()
file_basename=os.path.basename(args.dataset)
ana.output = "skimmed_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"
if "Data" in args.dataset:
    ana.output = "masked_skimmed_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"
ana.snapshot()
ana.save_fileInfo()
ana.save_cutflowInfo()
