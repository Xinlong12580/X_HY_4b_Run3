operation=$1
input=$2
output=inputArgs/"$operation"_args.txt
> $output
if [[ $operation == "skim" ]] ; then
    files=raw_nano/files/*.txt
    n_files_base=2
else
    files=outputList/"${input^^}"*.txt
    n_files_base=10000
fi
for file in $files; do
    
    if [[ $operation == *"selection"* && $file == *"QCD"* ]] ; then
        n_files=2
    else
        n_files=$n_files_base
    fi
        
    pass=0
    if [[ "$file" != *"SignalMC"* ]]; then
        pass=1
    elif [[ "$file" == *"MX-3000_MY-300"* ]]; then
        pass=1
    fi
    
    if [[ $pass == 1 ]]; then
        if [[ "$file" == *"2022__"* ]]; then
            ./gen_args.sh $file 2022 $output $n_files
        elif [[ "$file" == *"2022EE__"* ]]; then
            ./gen_args.sh $file 2022EE $output $n_files
        elif [[ "$file" == *"2023__"* ]]; then
            ./gen_args.sh $file 2023 $output $n_files
        elif [[ "$file" == *"2023BPix__"* ]]; then
            ./gen_args.sh $file 2023BPix $output $n_files
        fi
    fi
done
