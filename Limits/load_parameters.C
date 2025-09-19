void load_parameters(std::string in_file = "Control_MX-3000_MY-1000_workspace/SignalMC_XHY4b_1x1_area/higgsCombineSnapshot.MultiDimFit.mH125.root"){
    
	TFile *f_control = TFile::Open(in_file.c_str(), "READ");
	RooWorkspace w_control =* (RooWorkspace*) f_control->Get("w");
    w_control.loadSnapshot("MultiDimFit");
	RooArgSet v_control = w_control.allVars();
    std::ofstream outfile("control_parameters.txt");
	for (auto* arg : v_control) {
    	if (auto* var = dynamic_cast<RooRealVar*>(arg)) {
        	std::cout << var->GetName() << " = " << var->getVal() << std::endl;
            outfile << var->GetName() << " " << var->getVal() <<"\n";
        }
	}




}
