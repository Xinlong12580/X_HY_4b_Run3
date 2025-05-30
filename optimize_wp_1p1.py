from XHY4b_Analyzer import XHY4b_Analyzer
import ROOT
import TIMBER
TTBar_files = "nom_tagged_selected_SKIM_skimmed_2022__MC_TTBarJets__TTto4Q_ALL.root"
QCD_files = []
Signal_files = []
ana = XHY4b_Analyzer(TTBar_files, "2022", 1, 0 )
ana.output = "TTBar_optimze_wp.root"
ana.optimize_b_wp(0.3, 1, 0.1)
ana.snapshot()
ana.save_cutflowInfo()

