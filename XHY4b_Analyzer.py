import ROOT
import json
from hist import Hist
import array
import numpy as np
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer, Node
from TIMBER.Tools.AutoNoiseFilter import AutoNoiseFilter as AutoNF
from TIMBER.Tools.Common import CompileCpp, OpenJSON
import TIMBER.Tools.AutoJME_correctionlib as AutoJME
import TIMBER.Tools.AutoPU_correctionlib as AutoPU
import TIMBER.Tools.AutoBTagging_correctionlib as AutoBTagging

class XHY4b_Analyzer:
    #initiate the analyzer and set up the inputs
    def __init__(self, dataset = None, year = None, n_files = None, i_job = None, nEvents = -1):
        
        #set input variables
        self.dataset = dataset
        self.year = year
        self.n_files = n_files
        self.i_job = i_job
        self.nEvents = nEvents
        
        #loading json files contaning luminosity, Xsection and Trigger info
        with open("raw_nano/Luminosity.json") as f:        
            self.luminosity_json = json.load(f) 
        with open("raw_nano/Xsections_background.json") as f:
            self.Xsection_json = json.load(f)
        with open("raw_nano/Trigger.json") as f:
            self.Trigger_json = json.load(f)
        self.lumi =  self.luminosity_json[self.year]
        
        #Setting up the process, subprocess and Xsection of the job. For Signal the Xsection is set to 1 pb
        if "Signal" in self.dataset:
            self.Xsec = 1
            self.process = "SignalMC_XHY4b"
            self.subprocess = "SignalMC_XHY4b"
        elif "Data" in self.dataset:
            self.Xsec = 1
            self.process = "Data"
            self.subprocess = "Data"
        for process in self.Xsection_json:
            if process in self.dataset:
                self.process = process
                for subprocess in self.Xsection_json[process]:
                    if subprocess in self.dataset:
                        self.subprocess = subprocess
                        self.Xsec = self.Xsection_json[process][subprocess]

        #Setting up the year tag used in JME corrections
        self.triggers = self.Trigger_json["Hadron"][self.year]
        if self.year == "2022":
            self.corr_year = "2022_Summer22"
        elif self.year == "2022EE":
            self.corr_year = "2022_Summer22EE"
        elif self.year == "2023":
            self.corr_year = "2023_Summer23"
        elif self.year == "2023BPix":
            self.corr_year = "2023_Summer23BPix"

        #Setting default if no input args are provided
        if self.dataset == None:
            self.isData = -1
            self.files = None
            self.output = None
            self.analyzer = None
            self.totalWeight = {}
            return

        #Setting isData flag 
        if "Data" in self.dataset:
            self.isData = 1
        elif "MC" in self.dataset:
            self.isData = 0
        else:
            self.isData = -1
        
        #If the job is data, setting up the era used in JME corrections
        if self.isData == 1:
            eras = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
            for era in eras:
                if (era + "-") in self.dataset:
                    self.data_era = era
        else:
            self.data_era = ""

        #Setting up the default output root file. The Events snapshot, Runs Tree and Cutflow infomation will be stored in this file
        self.output = f"output_{self.n_files}_{self.i_job}.root"
        
        #instantiate a dictionary to store the cutflow infomation. The keys of this dict are the name of the step (cut) and the values are the total weight after the step. "genWeight" is used here.        
        self.totalWeight = {}

        #now that all the info for the job is set up, we start to build the analyzer. Firstly collect the the input files
        if ".root" in self.dataset:
            self.files=[self.dataset]
        
        elif ".txt" in self.dataset:
            with open(self.dataset, "r") as f:
                all_files = f.readlines()
                all_files = [line.strip() for line in all_files]
                N = len(all_files)
                job_files = []
                if (self.i_job * self.n_files) > (N - 1):
                    raise ValueError("i_job * n_files should be less than the total number of files") 
                if ((self.i_job + 1) * self.n_files) <= (N - 1):
                    job_files = all_files[self.i_job * self.n_files : (self.i_job + 1) * self.n_files]
                else:
                    job_files = all_files[self.i_job * self.n_files : N]
            self.files = []
            with open("raw_nano/BAD_ROOT_FILES.txt", "r") as f: #This function is no long in use
                self.bad_files = f.readlines()
                self.bad_files = [_file.strip().split() for _file in self.bad_files]
            for _file in job_files: #remove bad files
                if [self.dataset[(self.dataset.find("raw_nano/") + 9) : ], _file ] not in self.bad_files:
                    self.files.append(_file)
                    print(f"REGISTERING FILE: {self.dataset} {_file}")
                else:
                    print(f"IGNORING BAD FILE: {self.dataset} {_file}")
        else:
            raise ValueError("Input dataset must be a .txt or .root file") 
            

        if len(self.files) == 0:
                raise ValueError("No files are registered successfully") 
        
        #We collected the files and now build the analyzer 
        print(self.files) 
        self.analyzer = analyzer(self.files)
        self.analyzer.isData = self.isData
        if not (self.isData == 1):
            self.sumW = ROOT.RDataFrame("Runs", self.files).Sum("genEventSumw").GetValue()
        else:
            self.sumW = 1 
        if(nEvents > 0): 
            self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(100000, 100000 + nEvents))) # makes an RDF with only the first nentries considered
        return



 


    #register total weight after a certain step. This will be used to make the cutflow and efficiency plots. weight used is "genWeight"
    def register_weight(self, var, weight = "genWeight"):
        print(var)
        if self.isData == 1:
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Count().GetValue())
        else:
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Sum(weight).GetValue())
        print(self.totalWeight[var])
    

    #at the end of the job, we save the cutflow weights to the Cutflow TTree in the output root file
    def save_cutflowInfo(self):    
        print("saving cutflow.................") 
        in_file = ROOT.TFile.Open(self.files[0],"READ")    #Checking if the input files already contain the Cutflow tree. If so, sove it to the output file; if not, create a new Cutflow TTree
        cutflow_tree = in_file.Get("Cutflow")
        new_tree =  (len(self.files) > 1 or (not (cutflow_tree and isinstance(cutflow_tree, ROOT.TTree) and cutflow_tree.GetEntries() == 1))) #flag deciding if creating a new tree
        squashing = cutflow_tree and isinstance(cutflow_tree, ROOT.TTree) #flag if the new tree is should be built from beginning or squashed from existing entries
        in_file.Close()
        if new_tree:
            if squashing:
                print("squashing existing trees.................") 
                rdf_tmp = ROOT.RDataFrame("Cutflow", self.files)
                branches = rdf_tmp.GetColumnNames()
                
                sums = {branch: 0.0 for branch in branches}
                for branch in branches:
                    print("summing " + branch)
                    sums[branch] = rdf_tmp.Sum(branch).GetValue()
                for key in sums:
                    print(key, sums[key])
                #return
                tmp_file = ROOT.TFile.Open("tmp.root","RECREATE")    
                squashed_tree = ROOT.TTree("Cutflow", "Cutflow")
                out_vars = {}
                for branch in branches:
                    print(sums[branch])
                    vec = array.array('d', [sums[branch]])
                    out_vars[branch] = vec
                    
                    squashed_tree.Branch(f"{branch}", vec, f"{branch}/D")    
                    out_vars[branch][0] = sums[branch]
                squashed_tree.Fill()
                squashed_tree.SetDirectory(tmp_file)
                squashed_tree.Write()
                tmp_file.Close()
            else:
                print("creating tree.................") 
                tmp_file = ROOT.TFile.Open("tmp.root","RECREATE")    
                cutflow_tree = ROOT.TTree("Cutflow", "Cutflow")
                n_files = array.array('d', [float(len(self.files))])  
                cutflow_tree.Branch("n_files", n_files, "n_files/D")
                cutflow_tree.Fill()
                cutflow_tree.SetDirectory(tmp_file)
                cutflow_tree.Write()
                tmp_file.Close()
        if new_tree:
            cutflow_rdf = ROOT.RDataFrame("Cutflow", "tmp.root")
        else:
            cutflow_rdf = ROOT.RDataFrame("Cutflow", self.files)
        for w_name in self.totalWeight:
            cutflow_rdf = cutflow_rdf.Define(w_name, f"double({self.totalWeight[w_name]})")
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        cutflow_rdf.Snapshot("Cutflow", self.output, "", opts)
         


    #skimming function 
    def skim(self):
        #make skim cut
        self.register_weight("BeforeSkim")
        if self.totalWeight["BeforeSkim"] == 0:
            raise ValueError("file loading failed")
        #The SkimFlag contains both 1p1 and 2p1 events. for 1p1 the flag is 1 and 3; for 2p1 the flag is 2 and 3
        self.analyzer.Define("SkimFlag","skimFlag(nFatJet,FatJet_pt, FatJet_eta,FatJet_msoftdrop,nJet,Jet_pt, Jet_eta, nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId,Muon_miniIsoId)")
        
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        self.register_weight("Skim")



    #Generating tag to indicate is an event should be masked
    def mask_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Define("goldenJsonMask", f'mask_goldenJson("{self.year}", run, luminosityBlock)')
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 

    #Cut on Golden Json masking
    def cut_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Cut("goldenJsonCut", "goldenJsonMask == 1")
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 
        self.register_weight("GoldenJson")
         

   
    #main selection function for mode 1p1
    def selection_1p1(self, JME_syst = "nom"):
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")
        #Doing the skimming for 1p1
        self.analyzer.AddCorrection(
            Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
        )
        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")

        
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        

        
        #triggers
        hadron_triggers = self.triggers
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1_2FatJets")


        #FatJet quality
        self.analyzer.Cut("IDCut","FatJet_jetId[0] >= 2 && FatJet_jetId[1] >= 2")
        self.register_weight("FatJetID")
        
        #FatJet Pt
        self.analyzer.Cut("PtCut", f"FatJet_pt_{JME_syst}[0] > 450 && FatJet_pt_{JME_syst}[1] > 450")
        self.register_weight("FatJetPt")

        #FatJet Mass
        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 40 && FatJet_msoftdrop_{JME_syst}[1] > 40" )
        self.register_weight("FatJetMass")

        #FatJet Delta R
        self.analyzer.Cut("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        self.register_weight("DeltaEta")
        
        #Higgs Match
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")


    

        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 200")
        self.register_weight("MassJJ")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")

        self.analyzer.AddCorrection(
            Correction('triger_weight','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='corr'), {"pt":"leadingFatJetPt", "mass":"MX"}
        ) 
        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 

    




    #main selection function for mode 2p1
    def selection_2p1(self, JME_syst = "nom"):
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")
        self.analyzer.AddCorrection(
            Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
        ) 

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")


        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")
        
        #Looking for Higgs Jet
        self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Cut("HiggsEtaCut", "std::abs(EtaHiggsCandidate) < 2.5")
        self.register_weight("HiggsEta")

        self.analyzer.Cut("FatJetIDCut","FatJet_jetId[idxJH] >= 2 ")
        self.register_weight("FatJetID")


        self.analyzer.Cut("PtCut", f"PtHiggsCandidate > 300")
        self.register_weight(f"FatJetPt")
        

        #Defining several regions depending on the B tagging score for the Y Jets
        self.analyzer.Define("DeltaR_HJ", f"DeltaR(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH])")

        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], Jet_btagPNetB, 0.8)")
        self.analyzer.Cut("IdxJYCut", "idxJY[0] >= 0 && idxJY[1] >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY[0]")
        self.analyzer.Define("idxJY1", "idxJY[1]")  
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("PNet_Ymin", "std::min(PNet_Y0, PNet_Y1)")
        self.analyzer.Define("PNet_Y", "std::max(PNet_Y0, PNet_Y1)")




        self.analyzer.Cut("YJetIDCut", "Jet_jetId[idxJY0] >= 2 && Jet_jetId[idxJY1] >= 2")
        self.register_weight("YJetID")
        self.analyzer.Cut("YPtCut", "PtJY0 >= 50 && PtJY0 >= 50")
        self.register_weight("YPt")
        self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")

        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 200")
        self.register_weight("MXCut")
     
        self.analyzer.Cut("PNet_YminCut", "PNet_Ymin > 0.1")
        self.register_weight("PNet_Ymin")
        self.analyzer.Cut("MJYCut", "MassYCandidate > 200")
        self.register_weight("MJYCut")


        #defining a few variables
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassJJH")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        #Making weight columns
        self.analyzer.AddCorrection(
            Correction('triger_weight','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='corr'), {"pt":"leadingFatJetPt", "mass":"MX"}
        ) 
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 



    def selection_compound(self, JME_syst = "nom"):
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")
        self.analyzer.AddCorrection(
            Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
        ) 

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")

        #################################1p1####################################################################
        self.analyzer.Define("flag1p1_SkimCut", "SkimFlag == 1 || SkimFlag == 3") 

        #FatJet quality
        self.analyzer.Define("flag1p1_IDCut","FatJet_jetId[0] >= 2 && FatJet_jetId[1] >= 2")
        
        #FatJet Pt
        self.analyzer.Define("flag1p1_PtCut", f"FatJet_pt_{JME_syst}[0] > 450 && FatJet_pt_{JME_syst}[1] > 450")

        #FatJet Mass
        self.analyzer.Define("flag1p1_MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 40 && FatJet_msoftdrop_{JME_syst}[1] > 40" )

        #FatJet Delta R
        self.analyzer.Define("flag1p1_DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        
        #Higgs Match
        self.analyzer.Define("val1p1_idxH_try", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("val1p1_idxY_try", "1 - val1p1_idxH_try")
        self.analyzer.Define("val1p1_idxH", "std::max(0, val1p1_idxH_try)")
        self.analyzer.Define("val1p1_idxY", "std::min(1, val1p1_idxY_try)")
        self.analyzer.Define("flag1p1_HiggsCut", "val1p1_idxH_try >= 0") 


    
        #Defining a bunch of variables for later use
        self.analyzer.Define("val1p1_MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_PtHiggsCandidate", f"FatJet_pt_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_EtaHiggsCandidate", "FatJet_eta[val1p1_idxH]")
        self.analyzer.Define("val1p1_PhiHiggsCandidate", "FatJet_phi[val1p1_idxH]")
        self.analyzer.Define("val1p1_PNet_H", "FatJet_particleNet_XbbVsQCD[val1p1_idxH]")
        
        self.analyzer.Define("val1p1_MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_PtYCandidate", f"FatJet_pt_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_EtaYCandidate", "FatJet_eta[val1p1_idxY]")
        self.analyzer.Define("val1p1_PhiYCandidate", "FatJet_phi[val1p1_idxY]")
        self.analyzer.Define("val1p1_PNet_Y", "FatJet_particleNet_XbbVsQCD[val1p1_idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"val1p1_MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({val1p1_PtHiggsCandidate, val1p1_PtYCandidate}, {val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}, {val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}, {val1p1_MassHiggsCandidate, val1p1_MassYCandidate})")
        self.analyzer.Define("flag1p1_MJJCut", "val1p1_MassLeadingTwoFatJets > 200")


        
        self.analyzer.Define("val1p1_MJY", "val1p1_MassYCandidate")
        self.analyzer.Define("val1p1_MJJ", "val1p1_MassLeadingTwoFatJets")
        self.analyzer.Define("val1p1_MY", "val1p1_MassYCandidate")
        self.analyzer.Define("val1p1_MX", "val1p1_MassLeadingTwoFatJets")

        #######################################2p1########################################################## 
        #Skimming for 2p1
        self.analyzer.Define("flag2p1_SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        
        #Looking for Higgs Jet
        self.analyzer.Define("val2p1_idxJH_try", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Define("val2p1_idxJH", f"std::max(val2p1_idxJH_try, 0)")
        self.analyzer.Define("flag2p1_HiggsMassCut", f"val2p1_idxJH_try >= 0")

        
        self.analyzer.Define("val2p1_MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[val2p1_idxJH]")
        self.analyzer.Define("val2p1_PtHiggsCandidate", f"FatJet_pt_{JME_syst}[val2p1_idxJH]")
        self.analyzer.Define("val2p1_EtaHiggsCandidate", "FatJet_eta[val2p1_idxJH]")
        self.analyzer.Define("val2p1_PhiHiggsCandidate", "FatJet_phi[val2p1_idxJH]") 
        self.analyzer.Define("val2p1_PNet_H", "FatJet_particleNet_XbbVsQCD[val2p1_idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Define("flag2p1_HiggsEtaCut", "std::abs(val2p1_EtaHiggsCandidate) < 2.5")

        self.analyzer.Define("flag2p1_FatJetIDCut","FatJet_jetId[val2p1_idxJH] >= 2 ")


        self.analyzer.Define("flag2p1_PtCut", f"val2p1_PtHiggsCandidate > 300")
        

        #Defining several regions depending on the B tagging score for the Y Jets
        self.analyzer.Define("val2p1_DeltaR_HJ", f"DeltaR(Jet_eta, Jet_phi, FatJet_eta[val2p1_idxJH], FatJet_phi[val2p1_idxJH])")

        #Looking for Y Jets
        self.analyzer.Define("val2p1_idxJY_try", f"FindIdxJY(Jet_eta, Jet_phi, val2p1_EtaHiggsCandidate, val2p1_PhiHiggsCandidate, Jet_btagPNetB, 0.8)")
        self.analyzer.Define("val2p1_idxJY", "RVec<int>({std::max(val2p1_idxJY_try[0], 0), std::max(val2p1_idxJY_try[1], 0)})")
        self.analyzer.Define("flag2p1_IdxJYCut", "val2p1_idxJY_try[0] >= 0 && val2p1_idxJY_try[1] >= 0")


        #Defining a bunch of variables for later use
        self.analyzer.Define("val2p1_idxJY0", "val2p1_idxJY[0]")
        self.analyzer.Define("val2p1_idxJY1", "val2p1_idxJY[1]")  
        self.analyzer.Define("val2p1_PtJY0", f"Jet_pt_{JME_syst}[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PtJY1", f"Jet_pt_{JME_syst}[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_EtaJY0", "Jet_eta[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_EtaJY1", "Jet_eta[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PhiJY0", "Jet_phi[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PhiJY1", "Jet_phi[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_MassJY0", f"Jet_mass_{JME_syst}[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_MassJY1", f"Jet_mass_{JME_syst}[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PNet_Y0", "Jet_btagPNetB[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PNet_Y1", "Jet_btagPNetB[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PNet_Ymin", "std::min(val2p1_PNet_Y0, val2p1_PNet_Y1)")
        self.analyzer.Define("val2p1_PNet_Y", "std::max(val2p1_PNet_Y0, val2p1_PNet_Y1)")




        self.analyzer.Define("flag2p1_YJetIDCut", "Jet_jetId[val2p1_idxJY0] >= 2 && Jet_jetId[val2p1_idxJY1] >= 2")
        self.analyzer.Define("flag2p1_YPtCut", "val2p1_PtJY0 >= 50 && val2p1_PtJY0 >= 50")
        self.analyzer.Define("flag2p1_YEtaCut", "std::abs(val2p1_EtaJY0) < 2.5 && std::abs(val2p1_EtaJY1) < 2.5")
        
        
        self.analyzer.Define("val2p1_MassYCandidate", "InvMass_PtEtaPhiM({val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassJY0, val2p1_MassJY1} )" )
        self.analyzer.Define("val2p1_MassJJH", "InvMass_PtEtaPhiM({val2p1_PtHiggsCandidate, val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaHiggsCandidate, val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiHiggsCandidate, val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassHiggsCandidate, val2p1_MassJY0, val2p1_MassJY1})")
        self.analyzer.Define("flag2p1_MJJCut", "val2p1_MassJJH > 200")
     
        self.analyzer.Define("flag2p1_PNet_YminCut", "val2p1_PNet_Ymin > 0.1")
        self.analyzer.Define("flag2p1_MJYCut", "val2p1_MassYCandidate > 200")


        #defining a few variables
        self.analyzer.Define("val2p1_MJY", "val2p1_MassYCandidate")
        self.analyzer.Define("val2p1_MJJH", "val2p1_MassJJH")
        self.analyzer.Define("val2p1_MY", "val2p1_MassYCandidate")
        self.analyzer.Define("val2p1_MX", "val2p1_MassJJH")

        flagstring_1p1 = "1 "
        flagstring_2p1 = "1 "
        for c in self.analyzer.DataFrame.GetColumnNames():
            if "flag1p1" in  str(c):
                flagstring_1p1 += f"&& {str(c)} "
            if "flag2p1" in  str(c):
                flagstring_2p1 += f"&& {str(c)} "
        print(flagstring_1p1) 
        print(flagstring_2p1) 
        self.analyzer.Define("flag1p1", flagstring_1p1)
        self.analyzer.Define("flag2p1", flagstring_2p1)
        self.analyzer.Cut("flag1p1_or_flag2p1", "flag1p1 || flag2p1")
        self.register_weight("flag1p1_or_flag2p1")
        self.analyzer.AddCorrection(
            Correction('triger_1p1_weight','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='corr'), {"pt":"leadingFatJetPt", "mass":"val1p1_MX"}
        ) 
        self.analyzer.AddCorrection(
            Correction('triger_2p1_weight','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='corr'), {"pt":"leadingFatJetPt", "mass":"val2p1_MX"}
        ) 
        
        weights_1p1 = []
        weights_2p1 = []
        for c in self.analyzer.DataFrame.GetColumnNames():
            if "weight" in str(c) and "1p1" in str(c):
                weights_1p1.append(str(c))
            if "weight" in str(c) and "2p1" in str(c):
                weights_2p1.append(str(c))
        self.analyzer.MakeWeightCols(name = "1p1", dropList = weights_2p1)
        self.analyzer.MakeWeightCols(name = "2p1", dropList = weights_1p1)



    def eff_after_selection_2p1(self):
        wp_H_2p1 = 0.8
        wp_Y_2p1 = 0.8
        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_2p1", f"PNet_H > {wp_H_2p1} && PNet_Y > {wp_Y_2p1}") 
        self.register_weight("Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)

    def eff_after_selection_1p1(self):
        wp_H_1p1 = 0.98
        wp_Y_1p1 = 0.98
        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_1p1", f"PNet_H > {wp_H_1p1} && PNet_Y > {wp_Y_1p1}") 
        self.register_weight("Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)

    def eff_after_selection_compound(self): 
        wp_H_1p1 = 0.98
        wp_Y_1p1 = 0.98
        wp_H_2p1 = 0.8
        wp_Y_2p1 = 0.8
        self.analyzer.Define("flag1p1_Region_SR_1p1", f"flag1p1 && val1p1_PNet_H > {wp_H_1p1} && val1p1_PNet_Y > {wp_Y_1p1}")
        self.analyzer.Define("flag2p1_Region_SR_2p1", f"flag2p1 && val2p1_PNet_H > {wp_H_2p1} && val2p1_PNet_Y > {wp_Y_2p1}")

        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_1p1", "flag1p1_Region_SR_1p1") 
        self.register_weight("Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1", "flag2p1_Region_SR_2p1") 
        self.register_weight("Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_1p1_and_not_Region_SR_2p1", "flag1p1_Region_SR_1p1 && !(flag2p1_Region_SR_2p1)") 
        self.register_weight("Region_SR_1p1_and_not_Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1_and_not_Region_SR_1p1", "flag2p1_Region_SR_2p1 && !(flag1p1_Region_SR_1p1)") 
        self.register_weight("Region_SR_2p1_and_not_Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1_and_Region_SR_1p1", "flag2p1_Region_SR_2p1 && flag1p1_Region_SR_1p1") 
        self.register_weight("Region_SR_1p1_and_Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)





        



    #Defining Regions for mode 1p1
    def b_tagging_1p1(self):
        T_score_H = 0.98
        L_score_H = 0.95
        Aux_score1_H = 0.55
        Aux_score2_H = 0.3
        T_score_Y = 0.98
        L_score_Y = 0.95
        Aux_score1_Y = 0.55
        Aux_score2_Y = 0.3
        self.analyzer.Define("Region_SR1", f"PNet_H >= {T_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_SR2", f"PNet_H >= {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_SB1", f"PNet_H >= {T_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_SB2", f"PNet_H >= {L_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_VS1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS2", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_VS3", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS4", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB2", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y < {L_score_Y}")
    
    #defining Control and Validation regions in a different way
    def b_tagging_1p1_v1(self):
        T_score_H = 0.98
        L_score_H = 0.8
        Aux_score1_H = 0
        #Aux_score2_H = 0.3
        T_score_Y = 0.98
        L_score_Y = 0.8
        Aux_score1_Y = 0.55
        Aux_score2_Y = 0.3
        self.analyzer.Define("Region_SR1", f"PNet_Y >= {T_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_SR2", f"PNet_Y >= {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_SB1", f"PNet_Y >= {T_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_SB2", f"PNet_Y >= {L_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_VS1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS2", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_VS3", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS4", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB2", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H < {L_score_H}")
    
    #defining different regions for the 2p1 mode. Out-dated, should only use SR1, SR2, SB1 and SB2
    def b_tagging_2p1(self):
        T_score_H = 0.95
        L_score_H = 0.8
        Aux_score1_H = 0.5
        T_score_Y = 0.95
        L_score_Y = 0.8
        Aux_score1_Y = 0.7
        Aux_score2_Y = 0.5
        self.analyzer.Define("Region_SR1", f"PNet_Y >= {T_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_SR2", f"PNet_Y >= {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_SB1", f"PNet_Y >= {T_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
        self.analyzer.Define("Region_SB2", f"PNet_Y >= {L_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")

        self.analyzer.Define("Region_VS1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS2", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
        self.analyzer.Define("Region_VS3", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS4", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB2", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
    
    #Make cuts on a region
    def divide(self, region):
        self.analyzer.Cut(f"RegionCut_{region}","Region_" + region)
        self.register_weight("Region_"+region)
    



    #Saving 2D Hist MX vs MY for 1p1 mode. MY is saved as the x axis and MX the Y axis
    def dumpTemplates_1p1(self, region, f, JME_syst, weight = "weight_All__nominal"):
        f.cd()
        MJY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst == "nom":
            templates = self.analyzer.MakeTemplateHistos(
                ROOT.TH2D(f"MXvsMY_{region}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), 
                ['MY','MX']
        )
            templates.Do('Write')
        else:
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}_{JME_syst}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MY", "MX", weight)
            hist.Write()

    #Saving 2D Hist MX vs MY for 2p1 mode. MY is saved as the x axis and MX the Y axis
    def dumpTemplates_2p1(self, region, f, JME_syst, weight = "weight_All__nominal"):
        f.cd()
        MJY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst == "nom":
            templates = self.analyzer.MakeTemplateHistos(
                ROOT.TH2D(f"MXvsMY_{region}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), 
                ['MY','MX']
        )
            templates.Do('Write')
        else:
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}_{JME_syst}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MY", "MX", weight)
            hist.Write()


    def dumpTemplates_compound(self, region, f, JME_syst, mode = "1p1"):
        f.cd()
        MY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MX_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst != "nom":
            self.analyzer.Define(f"weight_{mode}__nominal_normalized", f"weight_{mode}__nominal/ {self.sumW}")
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__weight_{mode}__nominal_{JME_syst}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), "MY", "MX", f"weight_{mode}__nominal_normalized")
            hist.Write()
        else:
            for c in self.analyzer.DataFrame.GetColumnNames():
                if str(c).startswith("weight_")  and mode in str(c):
                    weight = str(c)
                    self.analyzer.Define(f"{weight}_normalized", f"{weight}/ {self.sumW}")
                    hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), "MY", "MX", f"{weight}_normalized")
                    hist.Write()
          


    #Saving a bunch of Hists where the column name and bins are specified in the "bins" dictionary, and weight given in the "weights" list
    def make_TH1(self, bins, weights, f):
        f.cd()
        for column in bins:
            if len(weights) == 0:
                hist = self.analyzer.DataFrame.Histo1D((f"{column}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", f"{column}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", len(bins[column]) - 1, bins[column]), column)
                hist.Write()
            else:
                for weight in weights:
                    hist = self.analyzer.DataFrame.Histo1D((f"{column}_{weight}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", f"{column}_{weight}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", len(bins[column]) - 1, bins[column]), column, weight)
                    hist.Write()


    def make_TH2(self, bins, weights, f, name = ""):
        f.cd()
        for graph in bins:
            it = iter(graph)
            x_name = next(it)
            y_name = next(it)
            x_bins = graph[x_name]
            y_bins = graph[y_name]
            if len(weights) == 0:
                hist = self.analyzer.DataFrame.Histo2D((f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", len(x_bins) - 1, x_bins, len(y_bins) - 1, y_bins ), x_name, y_name)
                hist.Write()
            else:
                for weight in weights:
                    hist = self.analyzer.DataFrame.Histo2D((f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", len(x_bins) - 1, x_bins, len(y_bins) - 1, y_bins ), x_name, y_name, weight)
                    hist.Write()

##############################################################################################################################
#For testing
#############################################################################################################################

    def selection_without_trigger_1p1(self, JME_syst = "nom"):
        #performing all the corrections
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")
        #Doing the skimming for 1p1
        
        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")

        
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        pre_trigger = ["HLT_PFJet260"]
        pretriggerCut = self.analyzer.GetTriggerString(pre_trigger)
        print(pretriggerCut)
        self.analyzer.Cut("PreTriggerCut", pretriggerCut)
        self.register_weight("PreTriggerCut")


        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1_2FatJets")


        #FatJet quality
        self.analyzer.Cut("IDCut","FatJet_jetId[0] >= 2 && FatJet_jetId[1] >= 2")
        self.register_weight("FatJetID")
        
        #FatJet Pt
        self.analyzer.Cut("PtCut", f"FatJet_pt_{JME_syst}[0] > 450 && FatJet_pt_{JME_syst}[1] > 450")
        self.register_weight("FatJetPt")

        #FatJet Mass
        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 40 && FatJet_msoftdrop_{JME_syst}[1] > 40" )
        self.register_weight("FatJetMass")

        #FatJet Delta R
        self.analyzer.Cut("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        self.register_weight("DeltaEta")
        
        #Higgs Match
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")


    

        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 200")
        self.register_weight("MassJJ")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")

        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 


    
    def add_trigger(self, triggers):
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        


    def selection_without_trigger_2p1(self, JME_syst = "nom"):
        #Performing all corrections
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        pre_trigger = ["HLT_PFJet260"]
        pretriggerCut = self.analyzer.GetTriggerString(pre_trigger)
        print(pretriggerCut)
        self.analyzer.Cut("PreTriggerCut", pretriggerCut)
        self.register_weight("PreTriggerCut")

        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")


        
        #Looking for Higgs Jet
        self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Cut("HiggsEtaCut", "std::abs(EtaHiggsCandidate) < 2.5")
        self.register_weight("HiggsEta")

        self.analyzer.Cut("FatJetIDCut","FatJet_jetId[idxJH] >= 2 ")
        self.register_weight("FatJetID")


        self.analyzer.Cut("PtCut", f"PtHiggsCandidate > 300")
        self.register_weight(f"FatJetPt")
        

        #Defining several regions depending on the B tagging score for the Y Jets
        self.analyzer.Define("DeltaR_HJ", f"DeltaR(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH])")

        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], Jet_btagPNetB, 0.8)")
        self.analyzer.Cut("IdxJYCut", "idxJY[0] >= 0 && idxJY[1] >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY[0]")
        self.analyzer.Define("idxJY1", "idxJY[1]")  
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("PNet_Ymin", "std::min(PNet_Y0, PNet_Y1)")
        self.analyzer.Define("PNet_Y", "std::max(PNet_Y0, PNet_Y1)")




        self.analyzer.Cut("YJetIDCut", "Jet_jetId[idxJY0] >= 2 && Jet_jetId[idxJY1] >= 2")
        self.register_weight("YJetID")
        self.analyzer.Cut("YPtCut", "PtJY0 >= 50 && PtJY0 >= 50")
        self.register_weight("YPt")
        self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")

        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 200")
        self.register_weight("MXCut")
     
        self.analyzer.Cut("PNet_YminCut", "PNet_Ymin > 0.1")
        self.register_weight("PNet_Ymin")
        self.analyzer.Cut("MJYCut", "MassYCandidate > 200")
        self.register_weight("MJYCut")


        #defining a few variables
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassJJH")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 






    #Making N-1 plots for the 1p1 mode
    def Nminus1_1p1(self, JME_syst, MC_weight, f): 
        f.cd()
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")
        #Doing the skimming for 1p1
        
        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")

        
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        

        
        #triggers and flags
        hadron_triggers = self.triggers
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1_2FatJets")


        #FatJet quality
        self.analyzer.Cut("IDCut","FatJet_jetId[0] >= 2 && FatJet_jetId[1] >= 2")
        self.register_weight("FatJetID")
        

        #FatJet Mass
        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 40 && FatJet_msoftdrop_{JME_syst}[1] > 40" )
        self.register_weight("FatJetMass")

        #Higgs Match
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")


    

        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 200")
        self.register_weight("MassJJ")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")

        self.analyzer.Define("FatJet_pt_0", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("FatJet_pt_1", f"FatJet_pt_{JME_syst}[1]")
        self.analyzer.Define("deltaEta", "abs(FatJet_eta[0] - FatJet_eta[1])")
        self.analyzer.MakeWeightCols(name = "All")
        NCuts = CutGroup("Nminus1_1p1")
        Vars = {}

        NCuts.Add("PtHCut", f"FatJet_pt_0 > 450 && FatJet_pt_1 > 450")
        Vars["PtHCut"] = {f"FatJet_pt_0":array.array("d", np.linspace(0, 3000, 301)), f"FatJet_pt_1":array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("DeltaEtaCut", "deltaEta < 1.3")
        Vars["DeltaEtaCut"] = {"deltaEta": array.array("d", np.linspace(0, 5, 101))}


        wp = 0.98
        NCuts.Add("BTaggingHCut", f"PNet_H >= {wp} && PNet_H >= {wp}") 
        Vars["BTaggingHCut"] = {f"PNet_H":array.array("d", np.linspace(0, 1, 101)), f"PNet_Y":array.array("d", np.linspace(0, 1, 101))}
        

        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()





    def Nminus1_2p1(self, JME_syst, MC_weight, f): #making N-1 plots for the 2p1 mode. Pretty out-dated, needs update beforing using
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")


        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")


        
        #Looking for Higgs Jet
        self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Cut("HiggsEtaCut", "std::abs(EtaHiggsCandidate) < 2.5")
        self.register_weight("HiggsEta")

        self.analyzer.Cut("FatJetIDCut","FatJet_jetId[idxJH] >= 2 ")
        self.register_weight("FatJetID")


        

        #Defining several regions depending on the B tagging score for the Y Jets
        self.analyzer.Define("DeltaR_HJ", f"DeltaR(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH])")

        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], Jet_btagPNetB, 0.8)")
        self.analyzer.Cut("IdxJYCut", "idxJY[0] >= 0 && idxJY[1] >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY[0]")
        self.analyzer.Define("idxJY1", "idxJY[1]")  
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("PNet_Ymin", "std::min(PNet_Y0, PNet_Y1)")
        self.analyzer.Define("PNet_Y", "std::max(PNet_Y0, PNet_Y1)")




        self.analyzer.Cut("YJetIDCut", "Jet_jetId[idxJY0] >= 2 && Jet_jetId[idxJY1] >= 2")
        self.register_weight("YJetID")
        self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")

        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 200")
        self.register_weight("MXCut")
     
        self.analyzer.Cut("PNet_YminCut", "PNet_Ymin > 0.1")
        self.register_weight("PNet_Ymin")
        self.analyzer.Cut("MJYCut", "MassYCandidate > 200")
        self.register_weight("MJYCut")


        #defining a few variables
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassJJH")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 


        NCuts = CutGroup("Nminus1_2p1")
        Vars = {}

        NCuts.Add("PtHCut", f"PtHiggsCandidate > 300")
        Vars["PtHCut"] = {f"PtHiggsCandidate":array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("PtJYCut", f"PtJY0 >= 50 && PtJY1 >= 50")
        Vars["PtJYCut"] = {f"PtJY0":array.array("d", np.linspace(0, 3000, 301)), f"PtJY1":array.array("d", np.linspace(0, 3000, 301))}
        wp_f = 0.8
        NCuts.Add("BTaggingHCut", f"PNet_H >= {wp_f}") 
        Vars["BTaggingHCut"] = {f"PNet_H":array.array("d", np.linspace(0, 1, 101))}
        wp_s = 0.8
        NCuts.Add("BTaggingYCut", f"PNet_Y >= {wp_s}") 
        Vars["BTaggingYCut"] = {f"PNet_Y":array.array("d", np.linspace(0, 1, 101))}
        
        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()
        
        
    

    
        
        
        
        




    def snapshot(self, columns = None, saveRunChain = False, openOption = "RECREATE"): #saving TTree to the output
        if columns == None:
            with open("raw_nano/columnBlackList.txt","r") as f:                                 
                badColumns = f.read().splitlines()
            with open("raw_nano/columnPrefixBlackList.txt","r") as f:                                 
                badColumnPrefixs = f.read().splitlines()
            with open("raw_nano/columnWhiteList.txt","r") as f:                                 
                goodColumns = f.read().splitlines()
            with open("raw_nano/columnPrefixWhiteList.txt","r") as f:                                 
                goodColumnPrefixs = f.read().splitlines()
                   
            columns = []                      
          
            for c in self.analyzer.DataFrame.GetColumnNames(): #defining default saving columns                
                passed = 1
                if c in badColumns:                                                      
                    passed = 0
                for bad_prefix in badColumnPrefixs:
                    if str(c).startswith(bad_prefix):
                        passed = 0
                
                if c in goodColumns: #The column list files have the highest prioroty
                    passed = 1 
                for good_prefix in goodColumnPrefixs:
                    if str(c).startswith(good_prefix):
                        passed = 1
                
                if passed == 1:                                                                    
                    columns.append(c)  
        for c in columns:
            print(c)
        print(f"Total number of columns: {len(columns)}")
        self.analyzer.Snapshot(columns, self.output, "Events", saveRunChain = saveRunChain, openOption = openOption)
    


    
    







































####################################################################################################################
#-----------------------TESTING , DEBUGGING, AND DEPRECATED FUNCTIONS------------------------------------------------------------
####################################################################################################################


    def save_fileInfo(self): #This function already exists in TIMBER
        run_rdf = ROOT.RDataFrame("Runs", self.files)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        run_rdf.Snapshot("Runs", self.output, "", opts)
    
        
    def optimize_b_wp(self, wp_min, wp_max, wp_step):
        for i in range(int(np.ceil((wp_max - wp_min) / wp_step)) + 1):
            wp = wp_min + i * wp_step
            self.analyzer.Cut(f"SRCut_wp_{wp:.4f}".replace(".", "p"), f"PNet_H >= {wp} && PNet_Y >= {wp}")
            self.register_weight(f"SRCut_wp_{wp:.4f}".replace(".", "p"))



    def lumiXsecWeight(self): #Other weighting schemes are used
        if self.isData == 0:
            luminosity = -1
            for year in self.luminosity_json:
                if (year + "__") in self.dataset:
                    luminosity = self.luminosity_json[year]
                    break
            if luminosity < 0:
                raise ValueError("Loading luminosity failed") 
                
            Xsection = -1
            for process in self.Xsection_json:
                if (process + "__") in self.dataset:
                    for subprocess in self.Xsection_json[process]:
                        print(subprocess)
                        if ((subprocess) in self.dataset):
                            Xsection = self.Xsection_json[process][subprocess]
                            break
                if Xsection >= 0:
                    break
            if Xsection < 0:
                raise ValueError("Loading Xsection failed")
              
            weightSum = ROOT.RDataFrame("Runs", self.files).Sum("genEventSumw").GetValue()
             
            print(f"reweightng MC samples {self.dataset} with luminosity {luminosity} and Xsection {Xsection}")
            self.analyzer.Define("lumiXsecWeight", f"lumiXsecWeight({luminosity}, {Xsection}, {weightSum}, genWeight)")
        else:
            raise ValueError("Weight can only e applied to MC files") 
        


        
         





    def make_analyzer(self):
        self.analyzer = analyzer(self.files)


    def Nminus1_1p1_old(self, JME_syst, MC_weight, f): 
        f.cd()
        AutoJME.AutoJME(self.analyzer, "FatJet", self.corr_year, self.data_era, True)
        print(self.isData)
        if not (self.isData == 1):
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

            AutoPU.AutoPU(self.analyzer, self.corr_year)
            #AutoBTagging.AutoBTagging(self.analyzer, self.corr_year, ijets = [0, 1])
        self.register_weight("JERCJetVeto")
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1")


        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")




        hadron_triggers = self.triggers
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        self.analyzer.Cut("TriggerCut", triggerCut)
        flagFilters = ["Flag_goodVertices", "Flag_globalSuperTightHalo2016Filter", "Flag_EcalDeadCellTriggerPrimitiveFilter", " Flag_BadPFMuonFilter", "Flag_BadPFMuonDzFilter", "Flag_hfNoisyHitsFilter", "Flag_eeBadScFilter"]
        flagFilterCut = self.analyzer.GetFlagString(flagFilters)
        self.analyzer.Cut("FlagCut", flagFilterCut)




        
        self.analyzer.Cut("IDCut","FatJet_jetId[0] > 1 && FatJet_jetId[1] > 1")



        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({FatJet_pt_" + JME_syst + "[0], FatJet_pt_" + JME_syst + "[1]}, {FatJet_eta[0], FatJet_eta[1]}, {FatJet_phi[0], FatJet_phi[1]}, {FatJet_msoftdrop_" + JME_syst + "[0], FatJet_msoftdrop_" + JME_syst + "[1]})")
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[std::max(idxH, 0)]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[std::min(idxY, 1)]")
        self.analyzer.Define(f"FatJet_pt_{JME_syst}_H", f"FatJet_pt_{JME_syst}[std::max(idxH, 0)]")
        self.analyzer.Define(f"FatJet_pt_{JME_syst}_Y", f"FatJet_pt_{JME_syst}[std::min(idxY, 1)]")
        self.analyzer.Define(f"FatJet_msoftdrop_{JME_syst}_H", f"FatJet_msoftdrop_{JME_syst}[std::max(idxH, 0)]")
        self.analyzer.Define(f"FatJet_msoftdrop_{JME_syst}_Y", f"FatJet_msoftdrop_{JME_syst}[std::min(idxY, 1)]")
        self.analyzer.Define("AbsDeltaEta", "abs(FatJet_eta[0] - FatJet_eta[1])")
        

        NCuts = CutGroup("Nminus1_1p1")
        Vars = {}

        NCuts.Add("PtHCut", f"FatJet_pt_{JME_syst}_H > 450")
        Vars["PtHCut"] = {f"FatJet_pt_{JME_syst}_H":array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("PtYCut", f"FatJet_pt_{JME_syst}_Y > 450")
        Vars["PtYCut"] = {f"FatJet_pt_{JME_syst}_Y":array.array("d", np.linspace(0, 3000, 301))}
        
        #NCuts.Add("MassHCut", f"FatJet_msoftdrop_{JME_syst}_H > 60")
        #Vars["MassHCut"] = {f"FatJet_msoftdrop_{JME_syst}_H": array.array("d", np.linspace(0, 5000, 501))}
        NCuts.Add("MassHCut", "idxH >= 0") 
        Vars["MassHCut"] = {f"FatJet_msoftdrop_{JME_syst}_H":array.array("d", np.linspace(0, 3000, 301))}        

        NCuts.Add("MassYCut", f"FatJet_msoftdrop_{JME_syst}_Y > 60")
        Vars["MassYCut"] = {f"FatJet_msoftdrop_{JME_syst}_Y": array.array("d", np.linspace(0, 5000, 501))}
        
        NCuts.Add("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        Vars["DeltaEtaCut"] = {"AbsDeltaEta": array.array("d", np.linspace(0, 6, 201) )}

        NCuts.Add("MJJCut", "MassLeadingTwoFatJets > 700")
        Vars["MJJCut"] = {"MassLeadingTwoFatJets": array.array("d", np.linspace(0, 5000, 501))}

        
        wp = 0.95
        NCuts.Add("BTaggingHCut", f"PNet_H >= {wp}") 
        Vars["BTaggingHCut"] = {f"PNet_H":array.array("d", np.linspace(0, 1, 101))}

        NCuts.Add("BTaggingYCut", f"PNet_Y >= {wp}") 
        Vars["BTaggingYCut"] = {f"PNet_Y":array.array("d", np.linspace(0, 1, 101))}

        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()




