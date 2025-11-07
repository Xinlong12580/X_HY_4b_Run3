#Running division for mode 1p1
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
args = parser.parse_args()
Veto_cuts = {"All1p1": "flag1p1", "All2p1" : "flag2p1", "Only1p1" : "flag1p1 && (! flag2p1)", "Only2p1": "flag2p1 && (! flag1p1)"}
#For each region, cut on the b score, then save the snapshot and cutflow and make 2D histograms
for veto_cut in Veto_cuts:

    #B tagging
    ana = XHY4b_Analyzer(args.dataset, args.year, args.n_files, args.i_job)

    #Specifying regions we want to save. each region is saved to one root file
    regions = ["SR1", "SR2", "SB1", "SB2", "VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]

    file_basename=os.path.basename(args.dataset).replace(".txt", f"_n-{args.n_files}_i-{args.i_job}.root")

    #Checking what JME correction the file has, cause we want to do the nom correction differently
    JME_systs = ["nom", "JES__up", "JES__down", "JER__up", "JER__down"]
    for ele in JME_systs:
        if ele in file_basename:
            JME_syst = ele
            break

    if "1p1" in veto_cut:
        mode = "1p1"
        ana.analyzer.Define("PNet_Y", "val1p1_PNet_Y")
        ana.analyzer.Define("PNet_H", "val1p1_PNet_H")
        ana.analyzer.Define("MX", "val1p1_MX")
        ana.analyzer.Define("MY", "val1p1_MY")
        ana.b_tagging_1p1()
    if "2p1" in veto_cut:
        mode = "2p1"
        ana.analyzer.Define("PNet_Y", "val2p1_PNet_Y")
        ana.analyzer.Define("PNet_H", "val2p1_PNet_H")
        ana.analyzer.Define("MX", "val2p1_MX")
        ana.analyzer.Define("MY", "val2p1_MY")
        ana.b_tagging_2p1()
    ana.analyzer.Cut(veto_cut, Veto_cuts[veto_cut])
    veto_base_node = ana.analyzer.GetActiveNode()
    ana.output = veto_cut + "_division_" + file_basename
    f = ROOT.TFile.Open("Templates_" + ana.output, "RECREATE")
    for region in regions:
        ana.analyzer.SetActiveNode(veto_base_node)
        ana.divide(region)
        #ana.output = veto_cut + "_" + region + "_" + file_basename
        print(ana.output)
        #ana.snapshot(saveRunChain = True)
        #ana.save_cutflowInfo()
        ana.dumpTemplates_compound(region, f, JME_syst,  mode ) 
        #f.Close()
    f.Close()


