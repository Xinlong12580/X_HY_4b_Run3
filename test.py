import ROOT
files=['root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-0.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-1.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-2.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-3.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-4.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-5.root', 'root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/nom_tagged_selected_SKIM_masked_skimmed_2023BPix__Data__JetMET1__Run2023D-22Sep2023_v2-v1__NANOAOD_n-4_i-6.root']
files = [files[0], files[1], files[2], files[3], files[4], files[5], files[6]]
#files = [files[0],  files[6]]
#files = [  files[6]]
rdf_tmp = ROOT.RDataFrame("Cutflow", files)
#a = rdf_tmp.Sum("BeforeSkim").GetValue()
#print(a)
branches = rdf_tmp.GetColumnNames()
#branches =["BeforeSkim"]         
sums = {branch: 0.0 for branch in branches}
print(sums)
for b in branches:
    branch = str(b)
    print(type(branch))
    print("summing " + branch)
    sums[branch] = rdf_tmp.Sum(branch).GetValue()
    #a = rdf_tmp.Sum(branch).GetValue()
for key in sums:
    print(key, sums[key])
    #return
