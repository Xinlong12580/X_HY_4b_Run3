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
args = parser.parse_args()

#cpp modules from Matej
CompileCpp("cpp_modules/deltaRMatching.cc")
CompileCpp("cpp_modules/helperFunctions.cc")
CompileCpp("cpp_modules/massMatching.cc")

CompileCpp("cpp_modules/selection_functions.cc")

#Specifying columns to save

#Running selection
ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)

bins = [{"leadingFatJetPt":array.array("d", np.linspace(0, 3000, 301)), "MassLeadingTwoFatJets": array.array("d", np.linspace(0, 5000, 501) ) }]
bins = [{"PtHiggsCandidate":array.array("d", np.linspace(0, 3000, 301)), "MJJH": array.array("d", np.linspace(0, 5000, 501) ) }]

file_basename = os.path.basename(args.dataset).removesuffix(".txt")
ana.output = file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"
#Saving the histograms to the "Templates" root file
f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH2(bins, ["weight_All__nominal"], f, "beforetrigger")
else:
    ana.make_TH2(bins, [], f)

ana.add_trigger(["HLT_AK8PFJet425_SoftDropMass40"])
if "MC" in ana.dataset:
    ana.make_TH2(bins, ["weight_All__nominal"], f, "aftertrigger")
else:
    ana.make_TH2(bins, [], f)
f.Close()
