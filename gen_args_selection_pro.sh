#Only run 2022EE samples and mass point MX-3000_MY-300
output=selection_args.txt
> $output
skim_files_data=$(eosls /store/user/xinlong/XHY4bRun3_2022_mask)
skim_files_MC=$(eosls /store/user/xinlong/XHY4bRun3_2022_lumiXsecWeight)
basedir_data='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_mask/'
basedir_MC='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_lumiXsecWeight/'
#for file in ${skim_files_data[@]}; do
#    ./gen_args_selection.sh $basedir_data$file 2022 $output
#done
for file in ${skim_files_MC[@]}; do
    ./gen_args_selection.sh $basedir_MC$file 2022 $output
done
