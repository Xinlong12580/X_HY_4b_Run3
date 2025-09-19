
void analyze()
{

    gROOT->SetBatch();  // don't need GUI popup
    using namespace RooFit; // YVar(), Binning() calls

    // Open the toys + GoF + snapshots file
    //TFile f("./SR1w_MX-800_MY-400_workspace/SignalMC_XHY4b_1x1_area/higgsCombine.AsymptoticLimits.mH125.123456.root", "READ");
    TFile f("root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_limits_2p1/higgsCombine.AsymptoticLimits.mH125.123456_1000_100_SB1_SR1.root", "READ");
        
    // Get the toys directory
    TDirectoryFile *toys = f.Get<TDirectoryFile>("toys");

    // Get the limit TTree (containing the saturated test statistic for each toy)
    TTree *limit = f.Get<TTree>("limit");

    // Get the actual limit (test statistic) branch from the limit tree
    Double_t lim;
    limit->SetBranchAddress("limit",&lim);

    // Create a file for saving the histograms
    TFile fOut("toy_histos.root", "RECREATE");
    fOut.cd();

    // Create a 2D histogram of test statistic vs # of events in toy data.
    TH2D *hOut = new TH2D("h_TestStat_vs_NEvents", "Saturated test statistic vs number of toy events;Saturated test statistic;Number toy events", 30, 0, 30, 5, 0, 5);

    // We also want to check the test statistic vs the input nuisance values for each toy, for the nuisances:
    //          QCD_uncert, QCD_comb, QCD_renorm, QCD_factrz, FSRunc, Pileup
    // These will mostly be constrained between -1 and 1, but we'll extend the range to [-2, 2] sigma
    TH2D *hQCD1 = new TH2D("h_TestStat_vs_QCDuncert", "Saturated test statistic vs QCD uncert toy nuisance input;Saturated test statistic;QCD_uncert_In", 30, 0, 30, 50, -5, 5);
    TH2D *hQCD2 = new TH2D("h_TestStat_vs_QCDcomb", "Saturated test statistic vs QCD comb toy nuisance input;Saturated test statistic;QCD_comb_In", 30, 0, 30, 50, -5, 5);
    TH2D *hQCD3 = new TH2D("h_TestStat_vs_QCDrenorm", "Saturated test statistic vs QCD renorm toy nuisance input;Saturated test statistic;QCD_renorm_In", 30, 0, 30, 50, -5, 5);
    TH2D *hQCD4 = new TH2D("h_TestStat_vs_QCDfactrz", "Saturated test statistic vs QCD factorization toy nuisance input;Saturated test statistic;QCD_factrz_In", 30, 0, 30, 50, -5, 5);
    TH2D *hFSR = new TH2D("h_TestStat_vs_FSRunc", "Saturated test statistic vs FSR uncert toy nuisance input;Saturated test statistic;FSRunc_In", 30, 0, 30, 50, -5, 5);
    TH2D *hPileup = new TH2D("h_TestStat_vs_Pileup", "Saturated test statistic vs Pileup uncert toy nuisance input;Saturated test statistic;Pileup_In", 30, 0, 30, 50, -5, 5);


    // Loop over all the toys. Divide number of keys by two b/c the snapshots for each toy are included
    for (int i=1; i<toys->GetNkeys()/2+1; i++) {
        // Open the RooDataSet
        std::cout << "Analyzing toy #" << i << "...." << std::endl;
        std::string s("toy_");
        //s += std::to_string(i);
        s = "toy_asimov";
        std::cout<<s<<std::endl;
        RooDataSet *rds = toys->Get<RooDataSet>(s.c_str());     // get the RooDataSet
        s += "_snapshot";
        RooArgSet  *ras = toys->Get<RooArgSet>(s.c_str());      // get the RooArgSet containing input nuisance parmaeter values
        rds->Print("V");
        //return; 

        // Set up binnings
        //std::vector<double> y_bins{625,725,825,925,1025,1125,1225,1325,1425,1525};
        //std::vector<double> x_bins{25,75,125,175,225,275,325,375,425,475,525,575,625,675,725,775,825};
        std::vector<double> y_bins{300, 400, 500, 600, 700, 800,900,1000,1100,1200,1300,1400,1600,2000,3000,4000, 5000};
        std::vector<double> x_bins{200, 300, 400, 500, 600, 700, 800, 900,1000,1100,1200,1300, 1400, 1600, 2000, 3000, 4000, 5000};
        RooBinning rb_y(y_bins.size() - 1, y_bins.data(), "rb_y");
        RooBinning rb_x(x_bins.size() - 1, x_bins.data(), "rb_x");

        // Reduce the RooDataSets
        std::unique_ptr<RooAbsData> low{rds->reduce("CMS_channel==CMS_channel::SR1_LOW")};
        std::unique_ptr<RooAbsData> sig{rds->reduce("CMS_channel==CMS_channel::SR1_SIG")};
        std::unique_ptr<RooAbsData> high{rds->reduce("CMS_channel==CMS_channel::SR1_HIGH")};

        // Make a histogram from one as a test
        RooArgSet const &dataVars = *rds->get();
        RooRealVar &xvarLow = static_cast<RooRealVar &>(dataVars["M_JY_LOW_default"]);
        RooRealVar &xvarSig = static_cast<RooRealVar &>(dataVars["M_JY_SIG_default"]);
        RooRealVar &xvarHigh = static_cast<RooRealVar &>(dataVars["M_JY_HIGH_default"]);
        RooRealVar &yvar = static_cast<RooRealVar &>(dataVars["M_JJ_default"]);
        TH1 *h_low = low->createHistogram("myhist_low", xvarLow, YVar(yvar, Binning(rb_y)), Binning(rb_x));
        TH1 *h_sig = sig->createHistogram("myhist_sig", xvarSig, YVar(yvar, Binning(rb_y)), Binning(rb_x));
        TH1 *h_high = high->createHistogram("myhist_high", xvarHigh, YVar(yvar, Binning(rb_y)), Binning(rb_x));

        // Save the histogram to the output file
        auto c1 = new TCanvas();
        h_low->Draw("COL Z");
        h_sig->Draw("SAME COL Z");
        h_high->Draw("SAME COL Z");
        //c1->Write(s.c_str());
        c1->Write();

        // Now calculate the number of events in this toy from the three LOW/SIG/HIGH histos
        int N = 0;
        N += h_low->Integral();
        N += h_sig->Integral();
        N += h_high->Integral();

        // Now get the value of the test statistic for this toy
        limit->GetEntry(i+1);   // add one because there are two identical entries per toy

        // Now fill the 2D histogram 
        hOut->Fill(lim, N);    

        // Print it out for good measure...
        std::cout << "\t(" << lim << ", " << N << ")" << std::endl;

        // Now let's get the RooRealVars for each of the nuisance parameter inputs for this toy.
        RooRealVar *QCD1 = dynamic_cast<RooRealVar*>(ras->find("QCD_uncert_In"));
        RooRealVar *QCD2 = dynamic_cast<RooRealVar*>(ras->find("QCD_comb_In"));
        RooRealVar *QCD3 = dynamic_cast<RooRealVar*>(ras->find("QCD_renorm_In"));
        RooRealVar *QCD4 = dynamic_cast<RooRealVar*>(ras->find("QCD_factrz_In"));
        RooRealVar *FSR  = dynamic_cast<RooRealVar*>(ras->find("FSRunc_In"));
        RooRealVar *PU   = dynamic_cast<RooRealVar*>(ras->find("Pileup_In"));

        // Now get the actual values
        double QCD1_v = QCD1->getValV();
        double QCD2_v = QCD2->getValV();
        double QCD3_v = QCD3->getValV();
        double QCD4_v = QCD4->getValV();
        double FSR_v  = FSR->getValV();
        double PU_v   = PU->getValV();

        // Now fill the respective histos
        hQCD1->Fill(lim, QCD1_v);
        hQCD2->Fill(lim, QCD2_v);
        hQCD3->Fill(lim, QCD3_v);
        hQCD4->Fill(lim, QCD4_v);
        hFSR->Fill(lim, FSR_v);
        hPileup->Fill(lim, PU_v);

    }

    // Save out the 2D histograms
    hOut->Write();
    hQCD1->Write();
    hQCD2->Write();
    hQCD3->Write();
    hQCD3->Write();
    hFSR->Write();
    hPileup->Write();


    fOut.Close();


    /*
    RooDataSet *rds = toys->Get<RooDataSet>("toy_1");

    // set up binnings
    std::vector<double> y_bins{625,725,825,925,1025,1125,1225,1325,1425,1525};
    std::vector<double> x_bins{25,75,125,175,225,275,325,375,425,475,525,575,625,675,725,775,825};
    RooBinning rb_y(y_bins.size() - 1, y_bins.data(), "rb_y");
    RooBinning rb_x(x_bins.size() - 1, x_bins.data(), "rb_x");

    // reduce the RooDataSets
    std::unique_ptr<RooAbsData> low{rds->reduce("CMS_channel==CMS_channel::SR_pass_LOW")};
    std::unique_ptr<RooAbsData> sig{rds->reduce("CMS_channel==CMS_channel::SR_pass_SIG")};
    std::unique_ptr<RooAbsData> high{rds->reduce("CMS_channel==CMS_channel::SR_pass_HIGH")};

    // make a histogram from one as a test
    RooArgSet const &dataVars = *rds->get();
    RooRealVar &xvarLow = static_cast<RooRealVar &>(dataVars["smass_LOW_default"]);
    RooRealVar &xvarSig = static_cast<RooRealVar &>(dataVars["smass_SIG_default"]);
    RooRealVar &xvarHigh = static_cast<RooRealVar &>(dataVars["smass_HIGH_default"]);
    RooRealVar &yvar = static_cast<RooRealVar &>(dataVars["tpmass_default"]);
    TH1 *h_low = low->createHistogram("myhist_low", xvarLow, YVar(yvar, Binning(rb_y)), Binning(rb_x));
    TH1 *h_sig = sig->createHistogram("myhist_sig", xvarSig, YVar(yvar, Binning(rb_y)), Binning(rb_x));
    TH1 *h_high = high->createHistogram("myhist_high", xvarHigh, YVar(yvar, Binning(rb_y)), Binning(rb_x));

    auto c1 = new TCanvas();
    h_low->Draw("COL Z");
    h_sig->Draw("SAME COL Z");
    h_high->Draw("SAME COL Z");
    c1->SaveAs("plot.png");
    */

}
