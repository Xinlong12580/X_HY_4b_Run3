#include "TIMBER/Framework/include/common.h"
#include "cpp_modules/share.h"

//Calculating DeltaR of two points
float DeltaR(RVec<float> Etas, RVec<float> Phies){
    float deltaEta = std::abs(Etas[0] - Etas[1]);
    float deltaPhi = std::abs(Phies[0]-Phies[1]) < M_PI ? std::abs(Phies[0] - Phies[1]) : 2*M_PI - std::abs(Phies[0] - Phies[1]);
    float deltaR=sqrt(deltaEta * deltaEta + deltaPhi * deltaPhi);
    return deltaR;
}

//Calculating DeltaR of each object in a collection with respect to a given point
RVec<float> DeltaR(RVec<float> Etas, RVec<float> Phies, float eta, float phi){
    if (Etas.size() != Phies.size())
        throw std::runtime_error("Eta vector and Phi vector should be of the same size");
    RVec<float> Delta_Rs = {};
    for (int i = 0; i < Etas.size(); i++){
        float deltaR = DeltaR({Etas.at(i), eta}, {Phies.at(i), phi});
        //std::cout<<deltaR<<std::endl;
        Delta_Rs.push_back(deltaR);
    }
    return Delta_Rs;
}

//2p1 mode only. Looking for two Y Jets satifying DeltaR and B score requirement
RVec<int> FindIdxJY(RVec<float> Etas, RVec<float> Phies, float eta, float phi, RVec<float> BScores, float deltaR){
    RVec<int> IdxJYs = {-1, -1};
    int count = 0;
    float max1 = -1;
    float max2 = -1;
    RVec<float> DeltaR_HJ = DeltaR(Etas, Phies, eta, phi);
    for (int i = 0; i < DeltaR_HJ.size(); i++)
    {
        if (DeltaR_HJ.at(i) <= deltaR)
            continue;
        if(BScores.at(i) > max1)
        {
            max1 = BScores.at(i);
            max2 = max1;
            IdxJYs.at(1) = IdxJYs.at(0);
            IdxJYs.at(0) = i;
        }
        else if (BScores.at(i) <= max1 && BScores.at(i) > max2)
        {
            max2 = i;
            IdxJYs.at(1) = i;
        } 

    }
    return IdxJYs; 
}

RVec<int> FindIdxJY(RVec<float> Etas, RVec<float> Phies, float eta, float phi, RVec<float> BScores, float deltaR, float minBScore, float maxBScore){
    RVec<int> IdxJYs = {-1, -1};
    int count = 0;
    RVec<float> DeltaR_HJ = DeltaR(Etas, Phies, eta, phi);
    for (int i = 0; i < DeltaR_HJ.size(); i++)
    {
        if (DeltaR_HJ.at(i) > deltaR && BScores.at(i) >= minBScore && BScores.at(i) < maxBScore )
        {
            IdxJYs.at(count) = i;
            count ++;
            if (count == 2)
                break;
        }
    }
    return IdxJYs; 
}
// 2p1 mode only. Looking for Higgs Jet from the first nmass FatJets, with mass requirement only
Int_t FindIdxJH(RVec<float> Masses, float minM, float maxM, int nMass){
    int ind_best = 0;
    float diff_mass_best = 10000;
    // Looking for best match
    for (int i = 0; i < Masses.size(); i++)
    {
        if (abs(Masses[i] - 125) < diff_mass_best) {
            ind_best = i;
            diff_mass_best = abs(Masses[i] - 125);
        }
    }
    //return best match
    float mass_best = Masses[ind_best];
    if (mass_best < maxM && mass_best > minM)
        return ind_best;
    else
	    return -1;
}



Int_t FindIdxJH_random(RVec<float> Masses, float minM, float maxM, int nMass){
    //Looking for all possible FatJets
    RVec<int> validIdxs = {};
    for (int i = 0; i < Masses.size(); i++)
    {
        if (i >= nMass) 
            break;
        if (Masses.at(i) >= minM && Masses.at(i) <= maxM)
            validIdxs.push_back(i);
    }
    //If there are more than one such FatJet, choose one randomly
    if (validIdxs.size() >= 1){
        std::random_device rd;                 
        std::mt19937 gen(rd());                
        std::uniform_int_distribution<> dist(0, validIdxs.size() - 1);  

        return validIdxs.at(dist(gen));
	}
    //if no FatJet found, return -1
	return -1;
}

bool calBadCalibFilterRecipe(int run,  float PuppiMET_pt, float PuppiMET_phi,  int nJet, RVec<float> Jet_pt, RVec<float> Jet_eta, RVec<float> Jet_phi, RVec<float> Jet_neEmEF, RVec<float> Jet_chEmEF) {
    if(run >= 362433 && run <= 367144){
        if (PuppiMET_pt > 100){
            for (int i = 0; i < nJet; i++){
                float deltaPhi = std::abs(Jet_phi[i] - PuppiMET_phi) < M_PI ? std::abs(Jet_phi[i] - PuppiMET_phi) : 2*M_PI - std::abs(Jet_phi[i] - PuppiMET_phi);
                if(Jet_pt[i] > 50 && Jet_eta[i] > -0.5 && Jet_eta[i] < -0.1 && (Jet_neEmEF[i] > 0.9 || Jet_chEmEF[i] > 0.9) && deltaPhi > 2.9)
                    return 0;
            }
        }
    }
    return 1;
}

//Calculate Inv mass for a list of variables
Float_t InvMass_PtEtaPhiM(ROOT::VecOps::RVec<Float_t> Pts, ROOT::VecOps::RVec<Float_t> Etas,  ROOT::VecOps::RVec<Float_t> Phis, ROOT::VecOps::RVec<Float_t> Masss)
{
	Float_t inv_mass = SHARE::InvalidF;
	RVec<ROOT::Math::PtEtaPhiMVector> Vectors = {};
	
	for(Int_t i = 0; i < Pts.size(); i++)
	{
		//If one value in the list is invalid, return invalid inv mass
		if(Pts.at(i) < (SHARE::InvalidF + 10) ||  Etas.at(i) < (SHARE::InvalidF + 10) || Phis.at(i) < (SHARE::InvalidF + 10) || Masss.at(i) < (SHARE::InvalidF + 10))
		{
			inv_mass = SHARE::InvalidF;
			return inv_mass;
		}
		
		ROOT::Math::PtEtaPhiMVector vector(Pts.at(i), Etas.at(i), Phis.at(i), Masss.at(i));
		Vectors.push_back(vector);
	}
	inv_mass = hardware::InvariantMass(Vectors);
	return inv_mass;
}
