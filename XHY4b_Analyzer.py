import ROOT
import json
from hist import Hist
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer, Node
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from TIMBER.Tools.AutoPU import ApplyPU, AutoPU

class XHY4b_Analyzer:
    def __init__(self, dataset = None, year = None, n_files = None, i_job = None, nEvents = -1):
        
        #set input variables
        self.dataset = dataset
        self.year = year
        self.n_files = n_files
        self.i_job = i_job
        self.nEvents = nEvents
        
        with open("raw_nano/Luminosity.json") as f:        
            self.luminosity_json = json.load(f) 
        with open("raw_nano/Xsections_background.json") as f:
            self.Xsection_json = json.load(f)
         
        #set default
        if self.dataset == None:
            self.isData = -1
            self.files = None
            self.output = None
            self.analyzer = None
            return

        if "Data" in self.dataset:
            self.isData = 1
        elif "MC" in self.dataset:
            self.isData = 0
        else:
            self.isData = -1
        ###self.output = self.dataset[9 : ] + f"_{self.n_files}_{self.i_job}.root"
        self.output = f"output_{self.n_files}_{self.i_job}.root"
        
        
        #extract input files and make analyzer
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
            with open("raw_nano/BAD_ROOT_FILES.txt", "r") as f:
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
         
        self.analyzer = analyzer(self.files)
        
        if(nEvents > 0): 
            #self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(nEvents))) # makes an RDF with only the first nentries considered
            self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(100000, 100000 + nEvents))) # makes an RDF with only the first nentries considered
        return



 
    def make_analyzer(self):
        self.analyzer = analyzer(self.files)
    
    def save_fileInfo(self):
        run_rdf = ROOT.RDataFrame("Runs", self.files)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        run_rdf.Snapshot("Runs", self.output, "", opts)
    
    def skim(self):
        #make skim cut
        nBeforeSkim = self.analyzer.GetActiveNode().DataFrame.Count().GetValue()
        self.analyzer.Define("nBeforeSkim", f"{nBeforeSkim}")
        self.analyzer.Define("SkimFlag","skimFlag(nFatJet,FatJet_eta,FatJet_pt,FatJet_msoftdrop,nJet,Jet_eta,Jet_pt,nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId,Muon_miniIsoId)")
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        nAfterSkim = self.analyzer.GetActiveNode().DataFrame.Count().GetValue()
        self.analyzer.Define("nAfterSkim", f"{nAfterSkim}")

    def mask_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Define("goldenJsonMask", f'mask_goldenJson("{self.year}", run, luminosityBlock)')
        else:
            raise ValueError("Golden json files can only e applied to data files") 
    
    def cut_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Cut("goldenJsonCut", "goldenJsonMask == 1")
        else:
            raise ValueError("Golden json files can only e applied to data files") 
         

    def lumiXsecWeight(self):
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
   
    def selection1(self):
        #self.analyzer.Cut("TwoFatJetsCut", "nFatJet >= 2")
        self.analyzer.Cut("TwoFatJetsCut", "skimmingTwoAK8Jets(nFatJet, FatJet_eta,  FatJet_pt, FatJet_msoftdrop) == 1")
        self.analyzer.Define("leadingFatJetPt", "FatJet_pt[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        
    def selection2(self):
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3") # it becones (B and not C) 
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        flagFilters = ["Flag_BadPFMuonFilter","Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_HBHENoiseIsoFilter","Flag_HBHENoiseFilter","Flag_globalSuperTightHalo2016Filter","Flag_goodVertices"]
        flagFilterCut = self.analyzer.GetFlagString(flagFilters)
        self.analyzer.Cut("FlagCut", flagFilterCut)
        
        self.analyzer.Cut("IDCut","FatJet_jetId[0] > 1 && FatJet_jetId[1] > 1")
        self.analyzer.Cut("PtCut", "FatJet_pt[0] > 450 && FatJet_pt[1] > 450")
        self.analyzer.Cut("MassCut", "FatJet_msoftdrop[0] > 60 && FatJet_msoftdrop[1] > 60")
        self.analyzer.Cut("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        self.analyzer.Define("MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({FatJet_pt[0], FatJet_pt[1]}, {FatJet_eta[0], FatJet_eta[1]}, {FatJet_phi[0], FatJet_phi[1]}, {FatJet_msoftdrop[0], FatJet_msoftdrop[1]})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 700")
        self.analyzer.Define("idxH", "higgsMassMatching(FatJet_msoftdrop[0], FatJet_msoftdrop[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.analyzer.Define("MassHiggsCandidate", "FatJet_msoftdrop[idxH]")
        self.analyzer.Define("PtHiggsCandidate", "FatJet_pt[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        
        self.analyzer.Define("MassYCandidate", "FatJet_msoftdrop[idxY]")
        self.analyzer.Define("PtYCandidate", "FatJet_pt[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        
        self.analyzer.Define("leadingFatJetPt", "FatJet_pt[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", "FatJet_msoftdrop[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 

    def b_tagging(self):
        T_score = 0.9
        L_score = 0.8
        Aux_score1 = 0.55
        Aux_score2 = 0.3
        self.analyzer.Define("Region_SR1", f"PNet_H >= {T_score} && PNet_Y >= {T_score}")
        self.analyzer.Define("Region_SR2", f"PNet_H >= {L_score} && PNet_Y >= {L_score}")
        self.analyzer.Define("Region_SB1", f"PNet_H >= {T_score} && PNet_Y < {L_score}")
        self.analyzer.Define("Region_SB2", f"PNet_H >= {L_score} && PNet_Y < {L_score}")
        self.analyzer.Define("Region_VS1", f"PNet_H >= {Aux_score1} && PNet_H < {L_score} && PNet_Y >= {T_score}")
        self.analyzer.Define("Region_VS2", f"PNet_H >= {Aux_score1} && PNet_H < {L_score} && PNet_Y >= {L_score}")
        self.analyzer.Define("Region_VB1", f"PNet_H >= {Aux_score1} && PNet_H < {L_score} && PNet_Y < {L_score}")
        self.analyzer.Define("Region_VS3", f"PNet_H >= {Aux_score2} && PNet_H < {Aux_score1} && PNet_Y >= {T_score}")
        self.analyzer.Define("Region_VS4", f"PNet_H >= {Aux_score2} && PNet_H < {Aux_score1} && PNet_Y >= {L_score}")
        self.analyzer.Define("Region_VB2", f"PNet_H >= {Aux_score2} && PNet_H < {Aux_score1} && PNet_Y < {L_score}")

    def divide(self, region):
        self.analyzer.Cut("RegionCut","Region_" + region)
    
    def snapshot(self, columns = None):
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
        for column in columns:
            print(column)
        print(len(columns))
        self.analyzer.Snapshot(columns, self.output, "Events")
    
        
        
        


        
         
