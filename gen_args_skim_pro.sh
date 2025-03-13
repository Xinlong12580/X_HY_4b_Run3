#Only run 2022EE samples and mass point MX-3000_MY-300
output=skim_args.txt
> $output
for file in raw_nano/files/*.txt; do
    pass=0
    if [[ "$file" == *"Summer22Nano"* &&  "$file" == *"MX-3000_MY-300"*  ]]; then
        pass=1
    elif [[ "$file" == *"Summer22Nano"* && ! ( "$file" == *"SignalMC_XHY4b"* ) ]]; then
        pass=1
    elif [[ "$file" == *2022_Data* ]]; then
        pass=1
    fi
    if [[ $pass == 1 ]]; then
        ./gen_args_skim.sh $file 2022EE $output 2
    fi
done
