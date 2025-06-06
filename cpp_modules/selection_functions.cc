#include "TIMBER/Framework/include/common.h"
#include "cpp_modules/share.h"
float DeltaR(RVec<float> Etas, RVec<float> Phies){
    float deltaEta = std::abs(Etas[0] - Etas[1]);
    float deltaPhi = std::abs(Phies[0]-Phies[1]) < M_PI ? std::abs(Phies[0] - Phies[1]) : 2*M_PI - std::abs(Phies[0] - Phies[1]);
    float deltaR=sqrt(deltaEta * deltaEta + deltaPhi * deltaPhi);
    return deltaR;
}


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

RVec<int> FindIdxJY(RVec<float> DeltaR_HJ, float deltaR = 1.2){
    RVec<int> IdxJYs = {-1, -1};
    int count = 0;
    for (int i = 0; i < DeltaR_HJ.size(); i++)
    {
        if (DeltaR_HJ.at(i) > deltaR)
        {
            IdxJYs.at(count) = i;
            count ++;
            if (count == 2)
                break;
        }
    }
    return IdxJYs; 
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
