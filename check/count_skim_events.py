import ROOT
with open("skim_1_output.txt") as f:
    lines = f.readlines()
    data_files =[("root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_skim_tmp_1/" + line.strip()) for line in lines]
counts = [0, 0, 0, 0] #2022, 2022EE, 2023, 2023BPix
for data_file in data_files:
    if "2022__Data" in data_file:
        print(data_file)
        rdf = ROOT.RDataFrame("Events", data_file)
        counts[0] += rdf.Count().GetValue()
    if "2022EE__Data" in data_file:
        print(data_file)
        rdf = ROOT.RDataFrame("Events", data_file)
        counts[1] += rdf.Count().GetValue()
    if "2023__Data" in data_file:
        print(data_file)
        rdf = ROOT.RDataFrame("Events", data_file)
        counts[2] += rdf.Count().GetValue()
    if "2023BPix__Data" in data_file:
        print(data_file)
        rdf = ROOT.RDataFrame("Events", data_file)
        counts[3] += rdf.Count().GetValue()
print(counts)
with open("_test_skim_count.txt","w") as f:
    for count in counts:
        f.write(f"{count}\n")
