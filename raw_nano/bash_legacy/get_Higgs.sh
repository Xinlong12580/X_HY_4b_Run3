data_label="MCHiggs"
files=(  /GluGluHto2B_M-125_TuneCP5_13p6TeV_powheg-minlo-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM
 /VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3/NANOAODSIM
 /WminusH_Hto2B_Wto2Q_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM
 /WplusH_Hto2B_Wto2Q_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM
 /ZH_Hto2B_Zto2Q_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM
 /ggZH_Hto2B_Zto2Q_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM
 /TTH_Hto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3/NANOAODSIM )
> bad_dataset_"$data_label".txt
for file in ${files[@]}; do
	Command="file dataset="$file
	data_name="$data_label""${file//\//_}"
	echo $Command
	echo dasgoclient -query "$Command"
	dasgoclient -query "$Command" | tee "$data_name"_tmp.txt
    sflag=$(tail -c 26 "$data_name"_tmp.txt)
    if [ "$sflag" = "unmatched dataset pattern" ]; then
	    echo "$data_name" >> bad_dataset.txt
    else
        sed 's@^@root://cmsxrootd.fnal.gov/@' "$data_name"_tmp.txt > "$data_name".txt
	fi
    rm "$data_name"_tmp.txt
done
