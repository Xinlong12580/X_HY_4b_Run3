'''
Script to generate ROOT files containing the TH2 inputs for 2DAlphabet from xinlong's pickle files.

The ROOT files will be of the form XYH4b_PROCESS_YEAR.root, and will contain histograms of the process and year of the form MJJvsMJY_REGION__nominal
'''
import pickle
import ROOT

years   = ['2022','2022EE','2023','2023BPix']
regions = ['VS1','VS2','VS3','VS4','VB1','VB2']

def write_TH2s(process, year, process_dict):
    print(f'Generating template ROOT file for {process}, {year}')
    out = ROOT.TFile.Open(f'rootfiles/XYH4b_{process}_{year}.root','RECREATE')
    out.cd()

    for region in regions:
        h = process_dict[region]
        h.SetName(f'MJJvsMJY_{region}__nominal')
        h.SetTitle(f'MJJ vs MJY {region} nominal')
        h.Write()

    out.Close()


# Load the pickle file
inPickle = '/uscms/home/xinlongl/nobackup/projects/XHY4bRun3/X_HY_4b_Run3/hists_division_2p1_TH.pkl'
with open(inPickle, "rb") as f:
    p = pickle.load(f)
    # We will just create ROOT files for each process and year separately. Each file will contain the distributions of that process for each region.
    for year in years:
        # First get the data for this region and year 
        data_dict = p['data'][year]
        write_TH2s('Data', year, data_dict)

        # Now get the backgrounds
        TTMC_dict = p['BKGs'][year]['MC_TTBarJets']
        TT_procs = list(TTMC_dict.keys())
        for TT_proc in TT_procs:
            TT_dict = TTMC_dict[TT_proc]
            write_TH2s(TT_proc, year, TT_dict)
        
        SignalMC_dict = p['BKGs'][year]['SignalMC_XHY4b']
        Signal_procs = list(SignalMC_dict.keys())
        for Signal_proc in Signal_procs:
            Signal_dict = SignalMC_dict[Signal_proc]
            write_TH2s(Signal_proc, year, Signal_dict)
