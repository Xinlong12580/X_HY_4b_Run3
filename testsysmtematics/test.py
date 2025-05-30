import ROOT
f = ROOT.TFile.Open("Templates_all.root", "READ")
for key in f.GetListOfKeys():
    hist = key.ReadObj()
    if isinstance(hist, ROOT.TH2):  
        hist_name = hist.GetName()
        if "JetMET" in hist.GetName():
            print(hist_name)
            print(hist.GetEntries())
