input_file=skim_args.txt
output_dir=/store/user/xinlong/XHY4bRun3_2022_skim_tmp
output_files=$(eosls $output_dir)
while IFS= read -r line; do
    #echo "$line"
    input_arg=$(echo "$line" | awk '{print $2}')
    input_base=$(basename $input_arg)
    output_base=$input_base
    if [[ $input_base == *.txt ]]; then
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        output_base="$input_base"_n-"$input_n"_i-"$input_i".root
    fi
    found=0
    for file in ${output_files[@]}; do
        if [[ $file == *"$output_base"* ]]; then
            found=1
            break
        fi
    done
    if [[ $found == 0 ]] ; then
        echo Missing $output_base
    fi
            
done < $input_file
