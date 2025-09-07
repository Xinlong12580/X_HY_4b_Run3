import ROOT
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
    TLorentzVector vec(float pt, float eta, float phi, float mass){
        TLorentzVector v;
        v.SetPtEtaPhiM(pt, eta, phi, mass);
        return v;
    }
""")
massX = "3000"
massY = "1000"
with open(DIR_TOP + f"raw_nano/files/2022EE__SignalMC_XHY4b__MX-{massX}_MY-{massY}.txt", "r") as f:
    files = [_file.strip() for _file in f.readlines()]
files = [files[0] ]
print(files)
rdf = ROOT.RDataFrame("Events", files)

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
