import ROOT
import json
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
        self.analyzer.Cut("TwoFatJetsCut", "nFatJet >= 2")
        self.analyzer.Define("leadingFatJetPt", "FatJet_pt[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        

    def snapshot(self, columns = None):
        if columns == None:
            with open("columnBlackList.txt","r") as f:                                 
                badColumns = f.read().splitlines()       
            columns = []                                
            for c in self.analyzer.DataFrame.GetColumnNames():
                if(str(c).startswith("HLT_")):
                    continue
                elif c in badColumns:                                                      
                    continue                                                               
                else:                                                                    
                    columns.append(c)  

        self.analyzer.Snapshot(columns, self.output, "Events")
