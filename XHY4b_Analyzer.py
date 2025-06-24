import ROOT
import json
from hist import Hist
import array
import numpy as np
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer, Node
from TIMBER.Tools.Common import CompileCpp, OpenJSON
import TIMBER.Tools.AutoJME_correctionlib as AutoJME
import TIMBER.Tools.AutoPU_correctionlib as AutoPU
import TIMBER.Tools.AutoBTagging_correctionlib as AutoBTagging

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
        with open("raw_nano/Trigger.json") as f:
            self.Trigger_json = json.load(f)
        self.lumi =  self.luminosity_json[self.year]
        
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
        self.triggers = self.Trigger_json["Hadron"][self.year]
        if self.year == "2022":
            self.corr_year = "2022_Summer22"
        elif self.year == "2022EE":
            self.corr_year = "2022_Summer22EE"
        elif self.year == "2023":
            self.corr_year = "2023_Summer23"
        elif self.year == "2023BPix":
            self.corr_year = "2023_Summer23BPix"

        #set default
        if self.dataset == None:
            self.isData = -1
            self.files = None
            self.output = None
            self.analyzer = None
            self.totalWeight = {}
            return

        if "Data" in self.dataset:
            self.isData = 1
        elif "MC" in self.dataset:
            self.isData = 0
        else:
            self.isData = -1
        
        if self.isData == 1:
            eras = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
            for era in eras:
                if (era + "-") in self.dataset:
                    self.data_era = era
        else:
            self.data_era = ""
        ###self.output = self.dataset[9 : ] + f"_{self.n_files}_{self.i_job}.root"
        self.output = f"output_{self.n_files}_{self.i_job}.root"
        
        
        self.totalWeight = {}
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
        print(self.files) 
        self.analyzer = analyzer(self.files)
        self.analyzer.isData = self.isData
        if not (self.isData == 1):
            self.sumW = ROOT.RDataFrame("Runs", self.files).Sum("genEventSumw").GetValue()
        
        if(nEvents > 0): 
            #self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(nEvents))) # makes an RDF with only the first nentries considered
            self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(100000, 100000 + nEvents))) # makes an RDF with only the first nentries considered
        return



 
    def make_analyzer(self):
        self.analyzer = analyzer(self.files)
    
    def register_weight(self, var, weight = "genWeight"):
        print(var)
        if self.isData == 1:
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Count().GetValue())
        else:
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Sum(weight).GetValue())
        print(self.totalWeight[var])
    
    def save_cutflowInfo(self):    
        print("saving cutflow.................") 
        in_file = ROOT.TFile.Open(self.files[0],"READ")    
        cutflow_tree = in_file.Get("Cutflow")
        new_tree =  (len(self.files) > 1 or (not (cutflow_tree and isinstance(cutflow_tree, ROOT.TTree) and cutflow_tree.GetEntries() == 1)))
        squashing = cutflow_tree and isinstance(cutflow_tree, ROOT.TTree)
        in_file.Close()
        if new_tree:
            if squashing:
                print("squashing existing tree.................") 
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
         


 
    def skim(self):
        #make skim cut
        self.register_weight("BeforeSkim")
        if self.totalWeight["BeforeSkim"] == 0:
            raise ValueError("file loading failed")
        self.analyzer.Define("SkimFlag","skimFlag(nFatJet,FatJet_pt, FatJet_eta,FatJet_msoftdrop,nJet,Jet_pt, Jet_eta, nElectron,Electron_cutBased,nMuon,Muon_looseId,Muon_pfIsoId,Muon_miniIsoId)")
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        self.register_weight("Skim")




    def mask_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Define("goldenJsonMask", f'mask_goldenJson("{self.year}", run, luminosityBlock)')
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 
    
    def cut_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Cut("goldenJsonCut", "goldenJsonMask == 1")
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 
        self.register_weight("GoldenJson")
         

   
        
    def selection_1p1(self, JME_syst = "nom"):
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
        self.register_weight("LeptonVeto")
        
        hadron_triggers = self.triggers
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        flagFilters = ["Flag_goodVertices", "Flag_globalSuperTightHalo2016Filter", "Flag_EcalDeadCellTriggerPrimitiveFilter", " Flag_BadPFMuonFilter", "Flag_BadPFMuonDzFilter", "Flag_hfNoisyHitsFilter", "Flag_eeBadScFilter"]
        flagFilterCut = self.analyzer.GetFlagString(flagFilters)
        self.analyzer.Cut("FlagCut", flagFilterCut)
        self.register_weight("FlagCut")
        
        self.analyzer.Cut("IDCut","FatJet_jetId[0] > 1 && FatJet_jetId[1] > 1")
        self.register_weight("FatJetID")
        self.analyzer.Cut("PtCut", f"FatJet_pt_{JME_syst}[0] > 450 && FatJet_pt_{JME_syst}[1] > 450")
        self.register_weight("FatJetPt")

        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 60 && FatJet_msoftdrop_{JME_syst}[1] > 60")
        self.register_weight("FatJetMass")
        self.analyzer.Cut("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        self.register_weight("DeltaEta")
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({FatJet_pt_" + JME_syst + "[0], FatJet_pt_" + JME_syst + "[1]}, {FatJet_eta[0], FatJet_eta[1]}, {FatJet_phi[0], FatJet_phi[1]}, {FatJet_msoftdrop_" + JME_syst + "[0], FatJet_msoftdrop_" + JME_syst + "[1]})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 700")
        self.register_weight("MassJJ")
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")

        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        
        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")

        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 

    def b_tagging_1p1(self):
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


    def optimize_b_wp(self, wp_min, wp_max, wp_step):
        for i in range(int(np.ceil((wp_max - wp_min) / wp_step)) + 1):
            wp = wp_min + i * wp_step
            self.analyzer.Cut(f"SRCut_wp_{wp:.4f}".replace(".", "p"), f"PNet_H >= {wp} && PNet_Y >= {wp}")
            self.register_weight(f"SRCut_wp_{wp:.4f}".replace(".", "p"))
        
        
        




    def dumpTemplates_1p1(self, region, f, JME_syst, weight = "weight_All__nominal"):
        f.cd()
        MJY_bins = array.array("d", np.linspace(0, 3000, 301) )
        MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst == "nom":
            templates = self.analyzer.MakeTemplateHistos(
                ROOT.TH2D(f"MJJvsMJY_{region}", f"MJJ vs MJY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), 
                ['MJY','MJJ']
        )
            templates.Do('Write')
        else:
            hist = self.analyzer.DataFrame.Histo2D((f"MJJvsMJY_{region}__{weight}_{JME_syst}", f"MJJ vs MJY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MJY", "MJJ", weight)
            hist.Write()



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

###########################################################################################

###################developping####################################################################

##########################################################################################
    def Nminus1_1p1(self, JME_syst, MC_weight, f):
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
        self.analyzer.Define("PNet_0", "FatJet_particleNet_XbbVsQCD[0]")
        self.analyzer.Define("PNet_1", "FatJet_particleNet_XbbVsQCD[1]")
        self.analyzer.Define(f"FatJet_pt_{JME_syst}_0", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define(f"FatJet_pt_{JME_syst}_1", f"FatJet_pt_{JME_syst}[1]")
        self.analyzer.Define(f"FatJet_msoftdrop_{JME_syst}_0", f"FatJet_msoftdrop_{JME_syst}[0]")
        self.analyzer.Define(f"FatJet_msoftdrop_{JME_syst}_1", f"FatJet_msoftdrop_{JME_syst}[1]")
        self.analyzer.Define("AbsDeltaEta", "abs(FatJet_eta[0] - FatJet_eta[1])")
        self.analyzer.MakeWeightCols(name = "All")
        

        NCuts = CutGroup("Nminus1_1p1")
        Vars = {}

        NCuts.Add("PtCut", f"FatJet_pt_{JME_syst}[0] > 450 && FatJet_pt_{JME_syst}[1] > 450")
        Vars["PtCut"] = {f"FatJet_pt_{JME_syst}_0":array.array("d", np.linspace(0, 3000, 301)), f"FatJet_pt_{JME_syst}_1": array.array("d", np.linspace(0, 3000, 301)) }

        NCuts.Add("MassCut", f"FatJet_msoftdrop_{JME_syst}[0] > 60 && FatJet_msoftdrop_{JME_syst}[1] > 60")
        Vars["MassCut"] = {f"FatJet_msoftdrop_{JME_syst}_0": array.array("d", np.linspace(0, 3000, 301)), f"FatJet_msoftdrop_{JME_syst}_1": array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("DeltaEtaCut", "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
        Vars["DeltaEtaCut"] = {"AbsDeltaEta": array.array("d", np.linspace(0, 6, 201) )}

        NCuts.Add("MJJCut", "MassLeadingTwoFatJets > 700")
        Vars["MJJCut"] = {"MassLeadingTwoFatJets": array.array("d", np.linspace(0, 5000, 501))}

        NCuts.Add("HiggsCut", "idxH >= 0") 
        Vars["HiggsCut"] = {f"FatJet_msoftdrop_{JME_syst}_0":array.array("d", np.linspace(0, 3000, 301)), f"FatJet_msoftdrop_{JME_syst}_1": array.array("d", np.linspace(0, 3000, 301))}        
        
        wp = 0.95
        NCuts.Add("BTaggingCut", f"PNet_0 >= {wp} && PNet_1 > {wp}") 
        Vars["BTaggingCut"] = {f"PNet_0":array.array("d", np.linspace(0, 1, 101)), f"PNet_1": array.array("d", np.linspace(0, 1, 101))}        


        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()

        
        

        
        
        

    def selection_2p1(self):
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        flagFilters = ["Flag_BadPFMuonFilter","Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_HBHENoiseIsoFilter","Flag_HBHENoiseFilter","Flag_globalSuperTightHalo2016Filter","Flag_goodVertices"]
        flagFilterCut = self.analyzer.GetFlagString(flagFilters)
        self.analyzer.Cut("FlagCut", flagFilterCut)
        self.register_weight("FlagCut")
        
        self.analyzer.Cut("IDCut","FatJet_jetId[0] > 1 ")
        self.register_weight("FatJetID")
        self.analyzer.Cut("PtCut", "FatJet_pt[0] > 450")
        self.register_weight("FatJetPt")
        self.analyzer.Cut("HiggsMassCut", "FatJet_msoftdrop[0] > 100 && FatJet_msoftdrop[0] < 150")
        self.register_weight("HiggsMatch")

        self.analyzer.Define("DeltaR_HJ", "DeltaR(Jet_eta, Jet_phi, FatJet_eta[0], FatJet_phi[0])")
        self.analyzer.Define("idxJY", "FindIdxJY(DeltaR_HJ, 1.2)")
        self.analyzer.Cut("IdxJYCut", "idxJY[0] >= 0 && idxJY[1] >= 0")
        self.register_weight("JYMatch")
        self.analyzer.Define("idxJY0", "idxJY[0]")
        self.analyzer.Define("idxJY1", "idxJY[1]")
        self.analyzer.Define("PtJY0", "Jet_pt[idxJY0]")
        self.analyzer.Define("PtJY1", "Jet_pt[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", "Jet_mass[idxJY0]")
        self.analyzer.Define("MassJY1", "Jet_mass[idxJY1]")
        self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")
        self.register_weight("JYPt")
        
        self.analyzer.Define("DeltaR_JJ", "DeltaR({EtaJY0, EtaJY1 }, {PhiJY0, PhiJY1 })")
        self.analyzer.Cut("DeltaRCut", "DeltaR_JJ > 0.4")
        self.register_weight("JYJYDeltaR")
        
        
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({FatJet_pt[0], PtJY0, PtJY1}, {FatJet_eta[0], EtaJY0, EtaJY1}, {FatJet_phi[0], PhiJY0, PhiJY1}, {FatJet_msoftdrop[0], MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 700")
        self.register_weight("MassJJH")
        self.analyzer.Define("MassHiggsCandidate", "FatJet_msoftdrop[0]")
        self.analyzer.Define("PtHiggsCandidate", "FatJet_pt[0]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[0]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[0]")
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[0]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 

    def b_tagging_2p1(self):
        T_score = 0.9
        L_score = 0.8
        Aux_score1 = 0.55
        Aux_score2 = 0.3
        self.analyzer.Define("PNet_Y", "std::min(PNet_Y0, PNet_Y1)")
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
        self.analyzer.Cut(f"RegionCut_{region}","Region_" + region)
        self.register_weight("Region_"+region)
    
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
        print(f"Total number of columns: {len(columns)}")
        self.analyzer.Snapshot(columns, self.output, "Events", saveRunChain = False, openOption='UPDATE')
    
    def save_fileInfo(self): #This function already exists in TIMBER
        run_rdf = ROOT.RDataFrame("Runs", self.files)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        run_rdf.Snapshot("Runs", self.output, "", opts)


    
    







































####################################################################################################################
#-----------------------TESTING AND DEPRECATED FUNCTIONS------------------------------------------------------------
####################################################################################################################


    
        
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
        


        
         
    def selection_1p1_test(self, JME_syst = "nom"):
        AutoJME.AutoJME(self.analyzer, "FatJet", self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": f"{self.sumW}"
            }
            self.analyzer.AddCorrection(genW, evalargs)

            AutoPU.AutoPU(self.analyzer, self.corr_year)
            #AutoBTagging.AutoBTagging(self.analyzer, self.corr_year, ijets = [0, 1])
        self.register_weight("Corrections")
        self.register_weight("SkimOf1p1")
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.register_weight("LeptonVeto")
        
        hadron_triggers = self.triggers
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.register_weight("TriggerCut")
        #flagFilters = ["Flag_BadPFMuonFilter","Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_HBHENoiseIsoFilter","Flag_HBHENoiseFilter","Flag_globalSuperTightHalo2016Filter","Flag_goodVertices"]
        flagFilters = ["Flag_goodVertices", "Flag_globalSuperTightHalo2016Filter", "Flag_EcalDeadCellTriggerPrimitiveFilter", " Flag_BadPFMuonFilter", "Flag_BadPFMuonDzFilter", "Flag_hfNoisyHitsFilter", "Flag_eeBadScFilter"]
        flagFilterCut = self.analyzer.GetFlagString(flagFilters)
        self.register_weight("FlagCut")
        
        self.register_weight("FatJetID")
        self.register_weight("FatJetPt")

        self.register_weight("FatJetMass")
        self.register_weight("DeltaEta")
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({FatJet_pt_" + JME_syst + "[0], FatJet_pt_" + JME_syst + "[1]}, {FatJet_eta[0], FatJet_eta[1]}, {FatJet_phi[0], FatJet_phi[1]}, {FatJet_msoftdrop_" + JME_syst + "[0], FatJet_msoftdrop_" + JME_syst + "[1]})")
        self.register_weight("MassJJ")
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1])")
        self.analyzer.Define("idxY", "1 - idxH")
        self.register_weight("HiggsMatch")

        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        
        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
