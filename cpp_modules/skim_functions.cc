using namespace ROOT::VecOps;

// 1p1 mode
int skimmingTwoAK8Jets(int nFatJet, RVec<float> FatJet_pt, RVec<float> FatJet_eta, RVec<float> FatJet_msoftdrop){
    if(nFatJet<2){
        return 0;
    }
    int pt_cut = FatJet_pt[0]>300 && FatJet_pt[1]>300;
    int eta_cut = TMath::Abs(FatJet_eta[0])<2.5 && TMath::Abs(FatJet_eta[1])<2.5;
    int mSD_cut = FatJet_msoftdrop[0]>30 && FatJet_msoftdrop[1]>30;
    
    if(pt_cut && eta_cut && mSD_cut){
        return 1;
    }
    else{
        return 0;
    }
}

// 2p1 mode. The Higgs could actually be the third or higher index FatJet, so may need to depricate the eta_mSD_cut here
int skimmingAK8JetwithTwoAK4Jets(int nFatJet, RVec<float> FatJet_pt, RVec<float> FatJet_eta, RVec<float> FatJet_msoftdrop, int nJet, RVec<float> Jet_pt, RVec<float> Jet_eta){
    if(nFatJet < 1 || nJet < 2){
        return 0;
    }
    int pt_cut = FatJet_pt[0]>300 && Jet_pt[0]>50;
    int ind_extra = std::min(nFatJet - 1, 1);
    int eta_mSD_cut = (TMath::Abs(FatJet_eta[0])<2.5  && FatJet_msoftdrop[0]>30) || (TMath::Abs(FatJet_eta[ind_extra])<2.5  && FatJet_msoftdrop[ind_extra]>30) ;
    
    if(pt_cut && eta_mSD_cut){
        return 1;
    }
    else{
        return 0;
    }
}

//skimming
int skimFlag(int nFatJet, RVec<float> FatJet_pt, RVec<float> FatJet_eta, RVec<float> FatJet_msoftdrop, int nJet, RVec<float> Jet_pt, RVec<float> Jet_eta, int nElectron, RVec<int> Electron_cutBased, int nMuon, RVec<bool> Muon_looseId, RVec<char> Muon_pfIsoId, RVec<char> Muon_miniIsoId){
    Int_t jetSkim1  = skimmingTwoAK8Jets(nFatJet,FatJet_pt,FatJet_eta,FatJet_msoftdrop);
    Int_t jetSkim2  = skimmingAK8JetwithTwoAK4Jets(nFatJet,FatJet_pt,FatJet_eta,FatJet_msoftdrop, nJet, Jet_pt, Jet_eta);
    Int_t skimScore  = jetSkim1+2*jetSkim2;
    return skimScore;
}

