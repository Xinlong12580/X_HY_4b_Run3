import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from XHY4b_Analyzer import *
from argparse import ArgumentParser
import os

parser=ArgumentParser()
parser.add_argument('-d', type=str, dest='dataset',action='store', required=False)
parser.add_argument('-y', type=str, dest='year',action='store', required=False)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=False)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=False)
args = parser.parse_args()

dataset="raw_nano/files/2022__Data__JetHT__Run2022C-22Sep2023-v1__NANOAOD.txt"

CompileCpp("goldenJson_mask.cc")
CompileCpp("deltaRMatching.cc")
CompileCpp("helperFunctions.cc")
ana = XHY4b_Analyzer(dataset, 2022, 1, 0, 10000)
ana.output = "testmask.root"
#ana.skim()
ana.mask_goldenJson()
#ana.cut_goldenJson()
ana.snapshot()
ana.save_fileInfo()

#ana.skim()
#ana.snapshot()
#file_basename=os.path.basename(args.dataset)
#ana.output = "skimmed_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"
#ana.snapshot()
