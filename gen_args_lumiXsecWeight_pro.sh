#Only run 2022EE samples and mass point MX-3000_MY-300
output=lumiXsecWeight_args.txt
> $output
skim_files=$(eosls /store/user/xinlong/XHY4bRun3_2022_skim)
basedir='root://cmsxrootd.fnal.gov//store/user/xinlong/XHY4bRun3_2022_skim/'
for file in ${skim_files[@]}; do
    pass=0
    if [[ "$file" == *"2022__MC"*  ]]; then
        pass=1
    fi
    if [[ $pass == 1 ]]; then
        ./gen_args_lumiXsecWeight.sh $basedir$file 2022 $output
    fi
done
