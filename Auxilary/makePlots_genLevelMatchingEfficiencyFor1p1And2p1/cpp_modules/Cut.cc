Bool_t MaxCut(RVec<Float_t> Vals, Float_t thrshld, Int_t nRequired)
{
	if (Vals.size() < nRequired)
		return false;
       std::priority_queue<Float_t, RVec<Float_t>, std::greater<Float_t>> Maxs; //use a priority_queque tostrip the smallest variables
       for (auto val : Vals)
       {
	       Maxs.push(val);
	       if(Maxs.size() > nRequired)
		       Maxs.pop();
       }
       if(Maxs.top() >= thrshld)
	       return true;
       return false;
}
