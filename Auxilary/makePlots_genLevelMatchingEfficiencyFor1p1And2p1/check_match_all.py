import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from argparse import ArgumentParser
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
    ROOT::VecOps::RVec<int> find_b(ROOT::VecOps::RVec<int> pdgIds, ROOT::VecOps::RVec<int> motherIdxes, int pdgId = 35){
        ROOT::VecOps::RVec<int> idxes = {-1, -1};
        //std::cout<<"TEST0"<<std::endl;
        for (int i = 0; i < pdgIds.size(); i++){
            if(pdgIds.at(i) == 5 && motherIdxes.at(i) < pdgIds.size() && pdgIds.at(motherIdxes.at(i)) == pdgId){
                idxes.at(0) = i;
                break;
            }
        }
        //std::cout<<"TEST1"<<std::endl;
        for (int i = 0; i < pdgIds.size(); i++){
            if(pdgIds.at(i) == -5 && motherIdxes.at(i) < pdgIds.size() && pdgIds.at(motherIdxes.at(i)) == pdgId){
                idxes.at(1) = i;
                break;
            }
        }
        return idxes;
    }

    TLorentzVector vec(float pt, float eta, float phi, float mass){
        TLorentzVector v;
        v.SetPtEtaPhiM(pt, eta, phi, mass);
        return v;
    }
""")

CompileCpp("cpp_modules/XHY4b_Helper.cc")
CompileCpp("cpp_modules/selection_functions.cc")


parser=ArgumentParser()
parser.add_argument('--mx', type=str, dest='massX',action='store', required=True)
parser.add_argument('--my', type=str, dest='massY',action='store', required=True)
args = parser.parse_args()

massX = args.massX
massY = args.massY
'''
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
'''
with open(f"raw_nano/files/2022EE__SignalMC_XHY4b__MX-{massX}_MY-{massY}.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
files = [files[0] ]
print(files)
rdf = ROOT.RDataFrame("Events", files)
N_Before = rdf.Count().GetValue()
print(N_Before)
rdf = rdf.Define("gen_Y_idx", "find_part(GenPart_pdgId, 35)")
rdf = rdf.Define("gen_higgs_idx", "find_part(GenPart_pdgId, 25)")
rdf = rdf.Define("gen_bY_idxes", "find_b(GenPart_pdgId, GenPart_genPartIdxMother, 35)")
rdf = rdf.Define("gen_bHiggs_idxes", "find_b(GenPart_pdgId, GenPart_genPartIdxMother, 25)")
rdf = rdf.Filter("gen_Y_idx >= 0 && gen_higgs_idx >= 0 && gen_bY_idxes[0] >= 0 && gen_bY_idxes[1] >= 0 && gen_bHiggs_idxes[0] >= 0 && gen_bHiggs_idxes[1] >= 0")

rdf = rdf.Define("gen_mY", "GenPart_mass[gen_Y_idx]")
h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_FatJet_Y_mass", f"gen_MX{massX}_MY{massY}_FatJet_Y_mass", 400, 0, 4000), f"gen_mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_Y_mass.png")

rdf = rdf.Define("gen_mHiggs", "GenPart_mass[gen_higgs_idx]")
h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_FatJet_Higgs_mass", f"gen_MX{massX}_MY{massY}_FatJet_Higgs_mass", 400, 0, 4000), f"gen_mHiggs").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_Higgs_mass.png")


rdf = rdf.Define("gen_bY_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bY_idxes[0]], GenPart_eta[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bY_idxes[0]], GenPart_phi[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_pts", "ROOT::VecOps::RVec<float>({GenPart_pt[gen_bY_idxes[0]], GenPart_pt[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_ms", "ROOT::VecOps::RVec<float>({GenPart_mass[gen_bY_idxes[0]], GenPart_mass[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_mbbY", "InvMass_PtEtaPhiM(gen_bY_pts, gen_bY_etas, gen_bY_phis, gen_bY_ms)")
h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_bbY_mass", f"gen_MX{massX}_MY{massY}_bbY_mass", 400, 0, 4000), f"gen_mbbY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_bbY_mass.png")

rdf = rdf.Define("gen_bH_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bHiggs_idxes[0]], GenPart_eta[gen_bHiggs_idxes[1]]})")
rdf = rdf.Define("gen_bH_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bHiggs_idxes[0]], GenPart_phi[gen_bHiggs_idxes[1]]})")
rdf = rdf.Define("gen_bH_pts", "ROOT::VecOps::RVec<float>({GenPart_pt[gen_bHiggs_idxes[0]], GenPart_pt[gen_bHiggs_idxes[1]]})")
rdf = rdf.Define("gen_bH_ms", "ROOT::VecOps::RVec<float>({GenPart_mass[gen_bHiggs_idxes[0]], GenPart_mass[gen_bHiggs_idxes[1]]})")
rdf = rdf.Define("gen_mbbH", "InvMass_PtEtaPhiM(gen_bH_pts, gen_bH_etas, gen_bH_phis, gen_bH_ms)")
h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_bbH_mass", f"gen_MX{massX}_MY{massY}_bbH_mass", 400, 0, 4000), f"gen_mbbH").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_bbH_mass.png")







rdf = rdf.Define("gen_higgs_eta", "GenPart_eta[gen_higgs_idx]")
rdf = rdf.Define("gen_higgs_phi", "GenPart_phi[gen_higgs_idx]")
rdf = rdf.Define("gen_Y_eta", "GenPart_eta[gen_Y_idx]")
rdf = rdf.Define("gen_Y_phi", "GenPart_phi[gen_Y_idx]")
rdf = rdf.Define("gen_bHiggs_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bHiggs_idxes[0]], GenPart_eta[gen_bHiggs_idxes[1]]})")
rdf = rdf.Define("gen_bHiggs_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bHiggs_idxes[0]], GenPart_phi[gen_bHiggs_idxes[1]]})")
#rdf = rdf.Define("gen_bY_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bY_idxes[0]], GenPart_eta[gen_bY_idxes[1]]})")
#rdf = rdf.Define("gen_bY_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bY_idxes[0]], GenPart_phi[gen_bY_idxes[1]]})")
#rdf = rdf.Define("bY_idxes", "ROOT::VecOps::RVec<int>({genBMatching(gen_bY_etas[0], gen_bY_phis[0], Jet_eta, Jet_phi, 0.4), genBMatching(gen_bY_etas[1], gen_bY_phis[1], Jet_eta, Jet_phi, 0.4)})")
rdf = rdf.Define("higgs_idx", "genHiggsMatching_withPNet(gen_higgs_eta, gen_higgs_phi, FatJet_eta, FatJet_phi, 0.8, FatJet_msoftdrop, 100, 150, FatJet_particleNet_XbbVsQCD, 0.9, 1.1 )")
rdf = rdf.Define("Y_idx", f"genHiggsMatching_withPNet(gen_Y_eta, gen_Y_phi, FatJet_eta, FatJet_phi, 0.8, FatJet_msoftdrop, {0.8 * float(massY)}, {1.2 * float(massY)}, FatJet_particleNet_XbbVsQCD, 0.9, 1.1 )")

rdf = rdf.Define("bY_idxes", "ROOT::VecOps::RVec<int>({genBMatching_withPNet(gen_bY_etas[0], gen_bY_phis[0], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1), genBMatching_withPNet(gen_bY_etas[1], gen_bY_phis[1], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1)})")
rdf = rdf.Define("bHiggs_idxes", "ROOT::VecOps::RVec<int>({genBMatching_withPNet(gen_bHiggs_etas[0], gen_bHiggs_phis[0], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1), genBMatching_withPNet(gen_bHiggs_etas[1], gen_bHiggs_phis[1], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1)})")

rdf_1p0 = rdf.Filter("Y_idx >= 0")
N_After = rdf_1p0.Count().GetValue()
eff = N_After / N_Before
print("1p0", eff)
rdf_1p0 = rdf_1p0.Define("reco_mY", "FatJet_msoftdrop[Y_idx]")
h_com = rdf_1p0.Histo1D((f"gen_reco_MX{massX}_MY{massY}_FatJet_Y_mass", f"gen_reco_MX{massX}_MY{massY}_FatJet_Y_mass", 400, 0, 4000), f"reco_mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_reco_MX{massX}_MY{massY}_Y_mass.png")



#rdf_2p0 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 ")
rdf_2p0 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 && bY_idxes[0] != bY_idxes[1] ")
N_After = rdf_2p0.Count().GetValue()
eff = N_After / N_Before
print("2p0", eff)
rdf_2p0 = rdf_2p0.Define("bY_etas", "ROOT::VecOps::RVec<float>({Jet_eta[bY_idxes[0]], Jet_eta[bY_idxes[1]]})")
rdf_2p0 = rdf_2p0.Define("bY_pts", "ROOT::VecOps::RVec<float>({Jet_pt[bY_idxes[0]], Jet_pt[bY_idxes[1]]})")
rdf_2p0 = rdf_2p0.Define("bY_phis", "ROOT::VecOps::RVec<float>({Jet_phi[bY_idxes[0]], Jet_phi[bY_idxes[1]]})")
rdf_2p0 = rdf_2p0.Define("bY_ms", "ROOT::VecOps::RVec<float>({Jet_mass[bY_idxes[0]], Jet_mass[bY_idxes[1]]})")
rdf_2p0 = rdf_2p0.Define("reco_mY", "InvMass_PtEtaPhiM(bY_pts, bY_etas, bY_phis, bY_ms)")
h_com = rdf_2p0.Histo1D((f"gen_reco_MX{massX}_MY{massY}_Y_mass", f"gen_reco_MX{massX}_MY{massY}_Y_mass", 400, 0, 4000), f"reco_mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_reco_MX{massX}_MY{massY}_bbY_mass.png")

#rdf_0p2 = rdf.Filter("bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0")
rdf_0p2 = rdf.Filter("bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0 && bHiggs_idxes[0] != bHiggs_idxes[1]")
N_After = rdf_0p2.Count().GetValue()
eff = N_After / N_Before
print("0p2", eff)
rdf_0p2 = rdf_0p2.Define("bY_etas", "ROOT::VecOps::RVec<float>({Jet_eta[bHiggs_idxes[0]], Jet_eta[bHiggs_idxes[1]]})")
rdf_0p2 = rdf_0p2.Define("bY_pts", "ROOT::VecOps::RVec<float>({Jet_pt[bHiggs_idxes[0]], Jet_pt[bHiggs_idxes[1]]})")
rdf_0p2 = rdf_0p2.Define("bY_phis", "ROOT::VecOps::RVec<float>({Jet_phi[bHiggs_idxes[0]], Jet_phi[bHiggs_idxes[1]]})")
rdf_0p2 = rdf_0p2.Define("bY_ms", "ROOT::VecOps::RVec<float>({Jet_mass[bHiggs_idxes[0]], Jet_mass[bHiggs_idxes[1]]})")
rdf_0p2 = rdf_0p2.Define("reco_mHiggs", "InvMass_PtEtaPhiM(bY_pts, bY_etas, bY_phis, bY_ms)")
h_com = rdf_0p2.Histo1D((f"gen_reco_MX{massX}_MY{massY}_Higgs_mass", f"gen_reco_MX{massX}_MY{massY}_Higgs_mass", 400, 0, 4000), f"reco_mHiggs").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_reco_MX{massX}_MY{massY}_bbHiggs_mass.png")

rdf_0p1 = rdf.Filter("higgs_idx >= 0")
N_After = rdf_0p1.Count().GetValue()
eff = N_After / N_Before
print("0p1", eff)
rdf_0p1 = rdf_0p1.Define("reco_mY", "FatJet_msoftdrop[higgs_idx]")
h_com = rdf_0p1.Histo1D((f"gen_reco_MX{massX}_MY{massY}_FatJet_higgs_mass", f"gen_reco_MX{massX}_MY{massY}_FatJet_higgs_mass", 400, 0, 4000), f"reco_mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_reco_MX{massX}_MY{massY}_Higgs_mass.png")


rdf_1p1 = rdf.Filter("Y_idx >= 0 && higgs_idx >= 0")
N_After = rdf_1p1.Count().GetValue()
eff = N_After / N_Before
print("1p1", eff)

#rdf_2p1 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 && higgs_idx >= 0")
rdf_2p1 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 && bY_idxes[0] != bY_idxes[1] && higgs_idx >= 0")
N_After = rdf_2p1.Count().GetValue()
eff = N_After / N_Before
print("2p1", eff)

#rdf_1p2 = rdf.Filter("Y_idx >= 0 && bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0")
rdf_1p2 = rdf.Filter("Y_idx >= 0 && bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0 && bHiggs_idxes[0] != bHiggs_idxes[1]")
N_After = rdf_1p2.Count().GetValue()
eff = N_After / N_Before
print("1p2", eff)

#rdf_2p2 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 && bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0")
rdf_2p2 = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0 && bHiggs_idxes[0] >= 0 && bHiggs_idxes[1] >= 0 && bY_idxes[0] != bY_idxes[1] && bHiggs_idxes[0] != bHiggs_idxes[1]")
N_After = rdf_2p2.Count().GetValue()
eff = N_After / N_Before
print("2p2", eff)


