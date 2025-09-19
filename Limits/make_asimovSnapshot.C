void make_asimovSnapshot(){
    
	TFile *f_control = TFile::Open("Control_MX-3000_MY-1000_workspace/SignalMC_XHY4b_1x1_area/higgsCombineSnapshot.MultiDimFit.mH125.root", "READ");
	RooWorkspace w_control =* (RooWorkspace*) f_control->Get("w");
    w_control.loadSnapshot("MultiDimFit");
	TFile *f_signal = TFile::Open("Loose_MX-3000_MY-1000_workspace/base.root", "READ");
	RooWorkspace w_signal =* (RooWorkspace*) f_signal->Get("w");
	RooArgSet v_signal = w_signal.allVars();
	RooArgSet v_control = w_control.allVars();
    std::cout<<"Signal"<<std::endl;
	v_signal.Print("v");
    std::cout<<"Control"<<std::endl;
	v_control.Print("v");
	for (auto* arg : v_control) {
    	if (auto* var = dynamic_cast<RooRealVar*>(arg)) {
        	std::cout << var->GetName() << " = " << var->getVal() << std::endl;
            if(std::string(var->GetName()).find("QCD") != std::string::npos)
                continue;
			if(auto* r2 = w_signal.var(var->GetName())){
				r2->setVal(var->getVal());
				r2->setConstant(var->isConstant());
				r2->setRange(var->getMin(), var->getMax());
			}
            else
            {
                w_signal.import(*var);
            }
    	}
	}
    std::cout<<"Signal"<<std::endl;
	for (auto* arg : w_signal.allVars()) {
    		if (auto* var = dynamic_cast<RooRealVar*>(arg)) {
        		std::cout << var->GetName() << " = " << var->getVal() << std::endl;
        }
    }
	RooArgSet allVars = w_signal.allVars();
	w_signal.saveSnapshot("mysnapshot", allVars);
	//w_signal.Print("t");
    w_signal.writeToFile("asimov_snapshot.root");
	//for (auto it = v_control.begin(); it != v_control.end(); it++ ) {
	//	auto* var = dynamic_cast<RooRealVar*>(it);	
	//	std::cout<<"1"<<std::endl;	
	//}




}
