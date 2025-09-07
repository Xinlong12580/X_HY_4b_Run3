import ROOT
import re

# Input txt file containing ROOT paths
#input_txt_path = "outputList/output_division_2p1.txt"
input_txt_path = "outputList/output_mass_debug_2p1.txt"

# Output efficiency file
output_file = "2p1_eff.txt"

# Open output file for writing
with open(output_file, "w") as out:
    # Open and read input file line by line
    with open(input_txt_path, "r") as filelist:
        for line in filelist:
            eos_path = line.strip()

            # Filter to only process ROOT files with required format
            if re.search(r"SR1.*nom.*2022EE__.*Signal", eos_path):
                # Extract MX and MY from filename
                mx_match = re.search(r"MX-(\d+)", eos_path)
                my_match = re.search(r"MY-(\d+)", eos_path)
                if not (mx_match and my_match):
                    print(f"Could not extract MX or MY from: {eos_path}")
                    continue

                MX = int(mx_match.group(1))
                MY = int(my_match.group(1))

                # Correct file path handling
                if eos_path.startswith("root://"):
                    file_path = eos_path
                else:
                    file_path = "root://cmsxrootd.fnal.gov" + eos_path

                try:
                    # Open ROOT file
                    f = ROOT.TFile.Open(file_path)
                    if not f or f.IsZombie():
                        print(f"Failed to open file: {file_path}")
                        continue

                    # Get Cutflow tree
                    cutflow = f.Get("Cutflow")
                    if not cutflow:
                        print(f"Cutflow tree not found in: {file_path}")
                        continue

                    # Load first entry
                    cutflow.GetEntry(0)

                    # Extract variables
                    #region_sr1 = getattr(cutflow, "Region_SR1", None)
                    region_sr1 = getattr(cutflow, "MJYCut", None)
                    before_skim = getattr(cutflow, "BeforeSkim", None)

                    # Check values exist and compute efficiency
                    if region_sr1 and before_skim and before_skim != 0:
                        eff = region_sr1 / before_skim
                        print(f"MX = {MX}, MY = {MY}, Efficiency = {eff:.6f}")
                        out.write(f"{MX} {MY} {eff:.6f}\n")
                    else:
                        print(f"Invalid values in: {file_path}")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

