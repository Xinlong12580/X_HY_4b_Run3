#Only run 2022EE samples and mass point MX-3000_MY-300
output=division_args.txt
> $output
#skim_files_data=$(eosls /store/user/xinlong/XHY4bRun3_2022_mask)
#skim_files_MC=$(eosls /store/user/xinlong/XHY4bRun3_2022_lumiXsecWeight)
#basedir_data='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_mask/'
#basedir_MC='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_lumiXsecWeight/'
#for file in ${skim_files_data[@]}; do
#    ./gen_args_selection.sh $basedir_data$file 2022 $output
#done
#for file in ${skim_files_MC[@]}; do
#    ./gen_args_selection.sh $basedir_MC$file 2022 $output
#done
selection_files=$(eosls /store/user/xinlong/XHY4bRun3_2022_selection2_hadded)
basedir='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection2_hadded/'
for file in ${selection_files[@]}; do
    if [[ "$file" != *"2022__"* ]]; then
        ./gen_args_division.sh $basedir$file 2022 VS1 $output
        ./gen_args_division.sh $basedir$file 2022 VS2 $output
        ./gen_args_division.sh $basedir$file 2022 VS3 $output
        ./gen_args_division.sh $basedir$file 2022 VS4 $output
        ./gen_args_division.sh $basedir$file 2022 VB1 $output
        ./gen_args_division.sh $basedir$file 2022 VB2 $output
    elif [[ "$file" != *"2022EE__"* ]]; then
        ./gen_args_division.sh $basedir$file 2022EE VS1 $output
        ./gen_args_division.sh $basedir$file 2022EE VS2 $output
        ./gen_args_division.sh $basedir$file 2022EE VS3 $output
        ./gen_args_division.sh $basedir$file 2022EE VS4 $output
        ./gen_args_division.sh $basedir$file 2022EE VB1 $output
        ./gen_args_division.sh $basedir$file 2022EE VB2 $output
    elif [[ "$file" != *"2023__"* ]]; then
        ./gen_args_division.sh $basedir$file 2023 VS1 $output
        ./gen_args_division.sh $basedir$file 2023 VS2 $output
        ./gen_args_division.sh $basedir$file 2023 VS3 $output
        ./gen_args_division.sh $basedir$file 2023 VS4 $output
        ./gen_args_division.sh $basedir$file 2023 VB1 $output
        ./gen_args_division.sh $basedir$file 2023 VB2 $output
    elif [[ "$file" != *"2023BPix__"* ]]; then
        ./gen_args_division.sh $basedir$file 2023BPix VS1 $output
        ./gen_args_division.sh $basedir$file 2023BPix VS2 $output
        ./gen_args_division.sh $basedir$file 2023BPix VS3 $output
        ./gen_args_division.sh $basedir$file 2023BPix VS4 $output
        ./gen_args_division.sh $basedir$file 2023BPix VB1 $output
        ./gen_args_division.sh $basedir$file 2023BPix VB2 $output
    fi
done
