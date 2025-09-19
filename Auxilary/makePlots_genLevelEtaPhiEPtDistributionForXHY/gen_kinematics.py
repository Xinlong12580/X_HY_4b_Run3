import ROOT
ROOT.gROOT.SetBatch(True)
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from argparse import ArgumentParser
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from XHY4b_Helper import *
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

CompileCpp(DIR_TOP + "cpp_modules/XHY4b_Helper.cc")
CompileCpp(DIR_TOP + "cpp_modules/selection_functions.cc")


massX = "2000"
massY = "1600"
with open(DIR_TOP + f"raw_nano/files/2022EE__SignalMC_XHY4b__MX-{massX}_MY-{massY}.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
files = [files[0] ]
print(files)
rdf = ROOT.RDataFrame("Events", files)

print(rdf.Count().GetValue())
rdf = rdf.Define("gen_Y_idx", "find_part(GenPart_pdgId, 35)")
rdf = rdf.Filter("gen_Y_idx >= 0")
rdf = rdf.Define("gen_bY_idxes", "find_b(GenPart_pdgId, GenPart_genPartIdxMother, 35)")
rdf = rdf.Filter("gen_bY_idxes[0] >= 0 && gen_bY_idxes[1] >= 0")
print(rdf.Count().GetValue())
rdf = rdf.Define("gen_bY_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bY_idxes[0]], GenPart_eta[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bY_idxes[0]], GenPart_phi[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_pts", "ROOT::VecOps::RVec<float>({GenPart_pt[gen_bY_idxes[0]], GenPart_pt[gen_bY_idxes[1]]})")
rdf = rdf.Define("gen_bY_ms", "ROOT::VecOps::RVec<float>({GenPart_mass[gen_bY_idxes[0]], GenPart_mass[gen_bY_idxes[1]]})")
rdf = rdf.Define("mY", "InvMass_PtEtaPhiM(gen_bY_pts, gen_bY_etas, gen_bY_phis, gen_bY_ms)")
h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_Y_mass", f"gen_MX{massX}_MY{massY}_Y_mass", 1000, -5000, 5000), f"mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_bbY_mass.png")
rdf = rdf.Define("bY_idxes", "ROOT::VecOps::RVec<int>({genBMatching_withPNet(gen_bY_etas[0], gen_bY_phis[0], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1), genBMatching_withPNet(gen_bY_etas[1], gen_bY_phis[1], Jet_eta, Jet_phi, 0.4, Jet_btagPNetB, 0.9, 1.1)})")
rdf = rdf.Filter("bY_idxes[0] >= 0 && bY_idxes[1] >= 0")
rdf = rdf.Define("bY_etas", "ROOT::VecOps::RVec<float>({Jet_eta[bY_idxes[0]], Jet_eta[bY_idxes[1]]})")
rdf = rdf.Define("bY_pts", "ROOT::VecOps::RVec<float>({Jet_pt[bY_idxes[0]], Jet_pt[bY_idxes[1]]})")
rdf = rdf.Define("bY_phis", "ROOT::VecOps::RVec<float>({Jet_phi[bY_idxes[0]], Jet_phi[bY_idxes[1]]})")
rdf = rdf.Define("bY_ms", "ROOT::VecOps::RVec<float>({Jet_mass[bY_idxes[0]], Jet_mass[bY_idxes[1]]})")
rdf = rdf.Define("reco_mY", "InvMass_PtEtaPhiM(bY_pts, bY_etas, bY_phis, bY_ms)")
h_com = rdf.Histo1D((f"reco_MX{massX}_MY{massY}_Y_mass", f"reco_MX{massX}_MY{massY}_Y_mass", 1000, -5000, 5000), f"reco_mY").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"reco_MX{massX}_MY{massY}_bbY_mass.png")

#exit()
#rdf = rdf.Define("bY_idxes", "ROOT::VecOps::RVec<int>({genBMatching(gen_bY_etas[0], gen_bY_phis[0], Jet_eta, Jet_phi, 0.4), genBMatching(gen_bY_etas[1], gen_bY_phis[1], Jet_eta, Jet_phi, 0.4)})")
rdf = rdf.Define("higgs_idx", "find_part(GenPart_pdgId, 25)")
rdf = rdf.Define("X_idx", "find_part(GenPart_pdgId, 45)")
rdf = rdf.Define("Y_idx", "find_part(GenPart_pdgId, 35)")
rdf = rdf.Filter("higgs_idx >= 0 && X_idx >= 0 && Y_idx >= 0")

rdf = rdf.Define("higgs_mass", "GenPart_mass[higgs_idx]")
rdf = rdf.Define("higgs_eta", "GenPart_eta[higgs_idx]")
rdf = rdf.Define("higgs_phi", "GenPart_phi[higgs_idx]")
rdf = rdf.Define("higgs_pt", "GenPart_pt[higgs_idx]")
rdf =rdf.Define("higgs_vec", "vec(higgs_pt, higgs_eta, higgs_phi, higgs_mass)")
rdf = rdf.Define("higgs_E", "higgs_vec.E()")
rdf = rdf.Define("higgs_Px", "higgs_vec.Px()")
rdf = rdf.Define("higgs_Py", "higgs_vec.Py()")
rdf = rdf.Define("higgs_Pz", "higgs_vec.Pz()")
rdf = rdf.Define("higgs_P", "sqrt(higgs_Px*higgs_Px + higgs_Py*higgs_Py + higgs_Pz*higgs_Pz)")

rdf = rdf.Define("X_mass", "GenPart_mass[X_idx]")
rdf = rdf.Define("X_eta", "GenPart_eta[X_idx]")
rdf = rdf.Define("X_phi", "GenPart_phi[X_idx]")
rdf = rdf.Define("X_pt", "GenPart_pt[X_idx]")
rdf =rdf.Define("X_vec", "vec(X_pt, X_eta, X_phi, X_mass)")
rdf = rdf.Define("X_E", "X_vec.E()")
rdf = rdf.Define("X_Px", "X_vec.Px()")
rdf = rdf.Define("X_Py", "X_vec.Py()")
rdf = rdf.Define("X_Pz", "X_vec.Pz()")

rdf = rdf.Define("Y_mass", "GenPart_mass[Y_idx]")
rdf = rdf.Define("Y_eta", "GenPart_eta[Y_idx]")
rdf = rdf.Define("Y_phi", "GenPart_phi[Y_idx]")
rdf = rdf.Define("Y_pt", "GenPart_pt[Y_idx]")
rdf = rdf.Define("Y_vec", "vec(Y_pt, Y_eta, Y_phi, Y_mass)")
rdf = rdf.Define("Y_E", "Y_vec.E()")
rdf = rdf.Define("Y_Px", "Y_vec.Px()")
rdf = rdf.Define("Y_Py", "Y_vec.Py()")
rdf = rdf.Define("Y_Pz", "Y_vec.Pz()")

rdf = rdf.Define("All_vec", "higgs_vec + Y_vec - X_vec")
rdf = rdf.Define("All_E", "All_vec.E()")
rdf = rdf.Define("All_Px", "All_vec.Px()")
rdf = rdf.Define("All_Py", "All_vec.Py()")
rdf = rdf.Define("All_Pz", "All_vec.Pz()")
parts = ["higgs", "X", "Y"]
for part in parts:
    h_mass = rdf.Histo1D((f"MX{massX}_MY{massY}_{part}_mass", f"MX{massX}_MY{massY}_{part}_mass", 500, 0, 5000), f"{part}_mass").GetValue()
    c = ROOT.TCanvas("c", "c")
    h_mass.Draw()
    c.Print(f"gen_MX{massX}_MY{massY}_{part}_mass.png")
    h_pt = rdf.Histo1D((f"MX{massX}_MY{massY}_{part}_pt", f"MX{massX}_MY{massY}_{part}_pt", 500, 0, 5000), f"{part}_pt").GetValue()
    c = ROOT.TCanvas("c", "c")
    h_pt.Draw()
    c.Print(f"gen_MX{massX}_MY{massY}_{part}_pt.png")

    h_eta = rdf.Histo1D((f"MX{massX}_MY{massY}_{part}_eta", f"MX{massX}_MY{massY}_{part}_eta", 100, -4, 4), f"{part}_eta").GetValue()
    c = ROOT.TCanvas("c", "c")
    h_eta.Draw()
    c.Print(f"gen_MX{massX}_MY{massY}_{part}_eta.png")
    
    h_phi = rdf.Histo1D((f"MX{massX}_MY{massY}_{part}_phi", f"MX{massX}_MY{massY}_{part}_phi", 100, -4, 4), f"{part}_phi").GetValue()
    c = ROOT.TCanvas("c", "c")
    h_phi.Draw()
    c.Print(f"gen_MX{massX}_MY{massY}_{part}_phi.png")
   
parts = ["higgs", "X", "Y", "All"] 
components = ["E", "Px", "Py", "Pz"]
for part in parts:
    for com in components:
        h_com = rdf.Histo1D((f"MX{massX}_MY{massY}_gen_{part}_{com}", f"MX{massX}_MY{massY}_gen_{part}_{com}", 1000, -5000, 5000), f"{part}_{com}").GetValue()
        c = ROOT.TCanvas("c", "c")
        h_com.Draw()
        c.Print(f"gen_MX{massX}_MY{massY}_{part}_{com}.png")

h_com = rdf.Histo1D((f"gen_MX{massX}_MY{massY}_higgs_P", f"gen_MX{massX}_MY{massY}_higgs_P", 1000, -5000, 5000), f"higgs_P").GetValue()
c = ROOT.TCanvas("c", "c")
h_com.Draw()
c.Print(f"gen_MX{massX}_MY{massY}_higgs_P.png")
