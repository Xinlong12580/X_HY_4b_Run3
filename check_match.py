import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
ROOT.gROOT.SetBatch(True)
ROOT.gInterpreter.Declare("""
    int find_part(ROOT::VecOps::RVec<int> pdgIds, int pdgId = 25){
        int idx = -1;
        for (int i = 0; i < pdgIds.size(); i++){
            if(pdgIds.at(i) == pdgId)
                idx = i;   
        }
        return idx;
    }
    TLorentzVector vec(float pt, float eta, float phi, float mass){
        TLorentzVector v;
        v.SetPtEtaPhiM(pt, eta, phi, mass);
        return v;
    }
""")

CompileCpp("cpp_modules/XHY4b_Helper.cc")

massX = "2000"
massY = "1600"
massXs = []
massYs = []
with open("raw_nano/GoodMassPoints.txt", "r") as f:
    for _file in f.readlines():
        _file = _file.strip()
        massXs.append(_file.partition(" ")[0])
        massYs.append(_file.partition(" ")[2])
for i in range(len(massXs)):
    print(massXs[i], "T", massYs[i])
exit()

with open(f"raw_nano/files/2022EE__SignalMC_XHY4b__MX-{massX}_MY-{massY}.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
files = [files[0] ]
print(files)
rdf = ROOT.RDataFrame("Events", files)
N_Before = rdf.Count().GetValue()
print(N_Before)
rdf = rdf.Define("higgs_idx", "find_part(GenPart_pdgId, 25)")
rdf = rdf.Filter("higgs_idx >= 0")
rdf = rdf.Define("higgs_eta", "GenPart_eta[higgs_idx]")
rdf = rdf.Define("higgs_phi", "GenPart_phi[higgs_idx]")
rdf = rdf.Define("HiggsIdx", "genHiggsMatching(higgs_eta, higgs_phi, FatJet_eta, FatJet_phi, 0.8, FatJet_msoftdrop, 90, 160 )")
rdf = rdf.Filter("HiggsIdx >= 0")
N_After = rdf.Count().GetValue()
print(N_After)
eff = N_After / N_Before
print(eff)




