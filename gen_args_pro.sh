operation=$1
input=$2
output="$operation"_args.txt
> $output
if [[ $operation == "skim" ]] ; then
    files=raw_nano/files/*.txt
    n_files_base=2
else
    files=outputList/"${input^^}"*.txt
    n_files_base=10000
fi
debug=0
if [[ $operation == *"debug"* ]] ; then
    debug=1
fi

for file in $files; do
    
    if [[ ( $operation == *"selection"* || $operation == *"Nminus1"* ) && ( $file == *"QCD"* ||  $file == *"Data"* ) ]] ; then
        n_files=2
    elif [[ ( $operation == *"selection"* || $operation == *"Nminus1"* ) && ( $file == *"TTBar"* || $file == *"WZ"* ) ]] ; then
        n_files=5
    else
        n_files=$n_files_base
    fi
        
    pass=0
    #if [[ "$file" == *"SignalMC"* ]]; then
    #    pass=1
    #elif [[ "$file" == *"MX-3000_MY-300"* ]]; then
    #    pass=1
    #fi
    if [[  $operation == *"Nminus1"* && "$file" == *"Data"* ]]; then
        pass=0
    fi 
    if [[ $file != *"2022EE"*"Signal"* ]]; then
        pass=0
    fi
    if [[ $file == *"Signal"* || $file == *"TTBar"* || $file == *"WZ"* || $file == *"Data"* ]]; then
        pass=1
    fi
    if [[ $debug == 1 ]]; then
        pass=0
        if [[ $file == *"Signal"* || $file == *"2022EE"* ]]; then
            pass=1
        fi
    fi
    echo $pass
    if [[ $operation == *"selection"* && $pass == 1 ]]; then
        extras=("-s nom" "-s JES__up" "-s JES__down" "-s JER__up" "-s JER__down")
        if [[ $debug == 1 ]]; then
            extras=("-s nom")
        fi
        for extra in "${extras[@]}"; do
            echo $extra
            if [[ $pass == 1 ]] ; then
                if [[ "$file" == *"2022__"* ]]; then
                    ./gen_args.sh $file 2022 $output $n_files "$extra"
                elif [[ "$file" == *"2022EE__"* ]]; then
                    ./gen_args.sh $file 2022EE $output $n_files "$extra"
                elif [[ "$file" == *"2023__"* ]]; then
                    ./gen_args.sh $file 2023 $output $n_files "$extra"
                elif [[ "$file" == *"2023BPix__"* ]]; then
                    ./gen_args.sh $file 2023BPix $output $n_files "$extra"
                fi
            fi
            if [[ $file == *"Data"* || $file == *"QCD"* ]]; then
                break
            fi
        done
    else
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
    fi
    
done
