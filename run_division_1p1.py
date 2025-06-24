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

ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)
ana.b_tagging_1p1()
regions = ["SR1", "SR2", "SB1", "SB2", "VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]

file_basename=os.path.basename(args.dataset).replace(".txt", f"_n-{args.n_files}_i-{args.i_job}.root")
JME_systs = ["nom", "JES__up", "JES__down", "JER__up", "JER__down"]
for ele in JME_systs:
    if ele in file_basename:
        JME_syst = ele
        break

#base_output_template = file_basename.partition("_202")[1] + file_basename.partition("_202")[2]
base_node = ana.analyzer.GetActiveNode()
for region in regions:
    ana.analyzer.SetActiveNode(base_node)
    ana.divide(region)
    ana.output = region + "_" + file_basename
    print(ana.output)
    ana.save_fileInfo()
    ana.save_cutflowInfo()
    ana.snapshot()
    f = ROOT.TFile.Open("Templates_" + ana.output, "RECREATE")
    ana.dumpTemplates_1p1(region, f, JME_syst) 
    f.Close()


