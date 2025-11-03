import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gInterpreter.Declare("""
    float find_max(ROOT::VecOps::RVec<float> values, int n){
    int _n = std::min(n, int(values.size()));
    if (_n != 0){
        auto maxIt = std::max_element(values.begin(), values.begin() + _n);
        return *maxIt;
    }
    else
        return -1;
    }
    int goodHiggs(ROOT::VecOps::RVec<float> Masses, ROOT::VecOps::RVec<float> BScores, float minMass = 100, float maxMass = 150, float minBScore = 0.95){
        for(int i = 0; i < Masses.size(); i++ ){
            if (Masses.at(i) < maxMass && Masses.at(i) > minMass && BScores.at(i) > minBScore){
                return i;
            }
        }
        return -1;
    }
""")

#files = [ "root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_2p1/nom_tagged_selected_2p1_SKIM_skimmed_2022EE__SignalMC_XHY4b__MX-2000_MY-500_n-10000_i-0.root", "root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_2p1/nom_tagged_selected_2p1_SKIM_skimmed_2022EE__SignalMC_XHY4b__MX-2000_MY-1600_n-10000_i-0.root"]
#files = ["root://cms-xrd-global.cern.ch//store/mc/Run3Summer22EENanoAODv12/NMSSM_XtoYHto4B_MX-2000_MY-500_TuneCP5_13p6TeV_madgraph-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2820000/efb5d01c-63fa-4a02-a01f-f853dcb0389a.root", "root://cms-xrd-global.cern.ch//store/mc/Run3Summer22EENanoAODv12/NMSSM_XtoYHto4B_MX-2000_MY-1600_TuneCP5_13p6TeV_madgraph-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/2820000/6c496b28-2ee0-446c-a7d1-ddcd0db70712.root"]
'''
files = []
with open("raw_nano/files/2022EE__SignalMC_XHY4b__MX-2000_MY-1600.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
rdf = ROOT.RDataFrame("Events", files)
#rdf = rdf.Filter("nFatJet > 0")
N_beforeCut  = rdf.Sum("genWeight").GetValue()
print(N_beforeCut)
#rdf = rdf.Define("PNet_H_max", "find_max(FatJet_particleNet_XbbVsQCD, 2)")
#rdf = rdf.Define("PNet_H_max", "find_max(FatJet_particleNetWithMass_HbbvsQCD, 2)")
#rdf = rdf.Filter("PNet_H_max > 0.95")
rdf = rdf.Define("goodHiggs", "goodHiggs(FatJet_mass, FatJet_particleNet_XbbVsQCD)")
rdf = rdf.Filter("goodHiggs > -0.5")
N_afterCut = rdf.Sum("genWeight").GetValue()
print(N_afterCut)
#print(_file, rdf.Mean("PNet_H").GetValue())
print(files, N_afterCut / N_beforeCut)
'''

mass = "1600"
idx = 0
files = []
with open(f"raw_nano/files/2022EE__SignalMC_XHY4b__MX-2000_MY-{mass}.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
rdf = ROOT.RDataFrame("Events", files)
rdf = rdf.Filter(f"nFatJet > {idx}")
rdf = rdf.Define("leadingMass", f"FatJet_mass[{idx}]")
#rdf = rdf.Define("leadingMass", f"FatJet_msoftdrop[{idx}]")
rdf = rdf.Define("leadingBScore", f"FatJet_particleNet_XbbVsQCD[{idx}]")
h_mass = rdf.Histo1D((f"leadingMass_{mass}", f"leadingMass_{mass}", 200, 0, 200), "leadingMass").GetValue()
c = ROOT.TCanvas("c", "c")
h_mass.Draw()
#c.Print(f"mosfdrop_MY{mass}_{idx}.png")
c.Print(f"mass_MY{mass}_{idx}.png")
h_BScore = rdf.Histo1D((f"leadingBScore_{mass}", f"leadingBScore_{mass}", 20, 0, 1), "leadingBScore").GetValue()
c = ROOT.TCanvas("c", "c")
h_BScore.Draw()
c.Print(f"BScore_MY{mass}_{idx}.png")
