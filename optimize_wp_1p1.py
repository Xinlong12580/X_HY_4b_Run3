from XHY4b_Analyzer import XHY4b_Analyzer
import ROOT
import TIMBER
import os
files = os.listdir("outputList")
files = ["outputList/" + f for f in files if "SELECTION" in f]
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = {"MC_QCDJets": [ "QCD-4Jets_HT-600to800", "QCD-4Jets_HT-800to1000", "QCD-4Jets_HT-1000to1200", "QCD-4Jets_HT-1200to1500", "QCD-4Jets_HT-1500to2000", "QCD-4Jets_HT-2000"], "MC_TTBarJets": ["TTto4Q", "TTtoLNu2Q", "TTto2L2Nu"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
for year in years:
    for process in processes:
        for subprocess in processes[process]:
            for f in files:
                if (process in f) and (subprocess in f) and ((year + "_") in f) and "nom" in f:
                    ana = XHY4b_Analyzer(f, "2022", 1000, 0 )
                    ana.output = f"optimize_wp/{year}_{process}_{subprocess}_optimze_wp.root"
                    ana.optimize_b_wp(0.93, 0.99, 0.001)
                    ana.snapshot()
                    ana.save_cutflowInfo()
                    break
    
