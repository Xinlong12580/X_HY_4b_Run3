import ROOT
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
        with open(self.dataset, "r") as f:
            all_files = f.readlines()
            all_files = [line.strip() for line in all_files]
            N = len(all_files)
            if (self.i_job * self.n_files) > (N - 1):
                raise ValueError("i_job * n_files should be less than the total number of files") 
            if ((self.i_job + 1) * self.n_files) <= (N - 1):
                self.files = all_files[self.i_job * self.n_files : (self.i_job + 1) * self.n_files]
            else:
                self.files = all_files[self.i_job * self.n_files : N]

        self.analyzer = analyzer(self.files)
        
        if(nEvents > 0): 
            self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(nEvents))) # makes an RDF with only the first nentries considered
        return



 
    def make_analyzer(self):
        self.analyzer = analyzer(self.files)

    def skim(self):
        
        #make skim cut
        nBeforeSkim = self.analyzer.GetActiveNode().DataFrame.Count().GetValue()
        self.analyzer.Define("nBeforeSkim", f"{nBeforeSkim}")
        self.analyzer.Define("SkimFlag","skimFlag(nFatJet,FatJet_eta,FatJet_pt,FatJet_msoftdrop,nJet,Jet_eta,Jet_pt,nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId,Muon_miniIsoId)")
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        nAfterSkim = self.analyzer.GetActiveNode().DataFrame.Count().GetValue()
        self.analyzer.Define("nAfterSkim", f"{nAfterSkim}")


    def snapshot(self):
        with open("columnBlackList.txt","r") as f:                                 
            badColumns = f.read().splitlines()       
        goodcols = []                                
        for c in self.analyzer.DataFrame.GetColumnNames():
            if(str(c).startswith("HLT_")):
                continue
            elif c in badColumns:                                                      
                continue                                                               
            else:                                                                    
                goodcols.append(c)  
        self.analyzer.Snapshot(goodcols, self.output, "Events")
