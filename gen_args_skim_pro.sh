#Only run 2022EE samples and mass point MX-3000_MY-300
output=skim_args.txt
> $output
for file in raw_nano/files/*.txt; do
    pass=0
    #if [[ "$file" != *"2022__"* &&  "$file" == *"MX-3000_MY-300"*  ]]; then
    #    pass=1
    #elif [[ "$file" != *"2022__"* && ! ( "$file" == *"SignalMC_XHY4b"* ) ]]; then
    #    pass=1
    #if [[ "$file" != *"2022__"* && ( "$file" == *Data* || "$file" == *QCD* || "$file" == *TTBarJets__TTto4Q* ) ]]; then
    #    pass=1
    #fi
    if [[ "$file" == *Data* ]]; then
        pass=1
    fi
    if [[ $pass == 1 ]]; then
        if [[ "$file" == *"2022__"* ]]; then
            ./gen_args_skim.sh $file 2022 $output 2
        elif [[ "$file" == *"2022EE__"* ]]; then
            ./gen_args_skim.sh $file 2022EE $output 2
        elif [[ "$file" == *"2023__"* ]]; then
            ./gen_args_skim.sh $file 2023 $output 2
        elif [[ "$file" == *"2023BPix__"* ]]; then
            ./gen_args_skim.sh $file 2023BPix $output 2
        fi
    fi
done
