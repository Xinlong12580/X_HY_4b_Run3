void check_asimovSnapshot(){
    
	TFile *f_control = TFile::Open("asimov_snapshot.root", "READ");
	RooWorkspace w_control =* (RooWorkspace*) f_control->Get("w");
	RooArgSet v_control = w_control.allVars();
	v_control.Print("v");
	for (auto* arg : v_control) {
    		if (auto* var = dynamic_cast<RooRealVar*>(arg)) {
        		std::cout << var->GetName() << " = " << var->getVal() << std::endl;
        }
    }
	//for (auto it = v_control.begin(); it != v_control.end(); it++ ) {
	//	auto* var = dynamic_cast<RooRealVar*>(it);	
	//	std::cout<<"1"<<std::endl;	
	//}




}
