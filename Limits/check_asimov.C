
int check_asimov(std::string MX, std::string MY)
{

    gROOT->SetBatch();  // don't need GUI popup
    using namespace RooFit; // YVar(), Binning() calls

    // Open the toys + GoF + snapshots file
    TFile f("root/tmp.root", "READ");
    //TFile f = TFile::Open("root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_limits_2p1/higgsCombine.AsymptoticLimits.mH125.123456_1000_100_SB1_SR1.root", "READ");
        
    // Get the toys directory
    TDirectoryFile *toys = f.Get<TDirectoryFile>("toys");

    // Get the limit TTree (containing the saturated test statistic for each toy)
    TTree *limit = f.Get<TTree>("limit");

    // Get the actual limit (test statistic) branch from the limit tree
    Double_t lim;
    limit->SetBranchAddress("limit",&lim);

    // Create a file for saving the histograms
    //TFile fOut("toy_histos.root", "UPDATE");
    TFile fOut("toy_histos.root", "RECREATE");
    fOut.cd();

    // Create a 2D histogram of test statistic vs # of events in toy data.
    TH2D *hOut = new TH2D("h_TestStat_vs_NEvents", "Saturated test statistic vs number of toy events;Saturated test statistic;Number toy events", 30, 0, 30, 5, 0, 5);


    // Loop over all the toys. Divide number of keys by two b/c the snapshots for each toy are included
        // Open the RooDataSet
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
        std::unique_ptr<RooAbsData> low{rds->reduce("CMS_channel==CMS_channel::SR2_LOW")};
        std::unique_ptr<RooAbsData> sig{rds->reduce("CMS_channel==CMS_channel::SR2_SIG")};
        std::unique_ptr<RooAbsData> high{rds->reduce("CMS_channel==CMS_channel::SR2_HIGH")};

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
        std::string name = "asimov_" + MX + "_" + MY;
        auto c_name = name.c_str();
        auto c1 = new TCanvas(c_name, c_name);
        h_low->Draw("COL Z");
        h_sig->Draw("SAME COL Z");
        h_high->Draw("SAME COL Z");
        //c1->Write(s.c_str());
        c1->Write();
        fOut.Close();
        return 1;
}
