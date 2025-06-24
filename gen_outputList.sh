mkdir -p outputList
classify_files(){
    input_dir=$1
    output_prefix=$2
    files=$( eosls $input_dir )
    prefix=$eosprefix$input_dir/
    declare -A classified_files
    for file in ${files[@]}; do
        if [[ $file == *"Templates"* || $file == *"output.log"* ]]; then
            continue
        fi
        if [[ $file = *.txt* ]]; then
            file_base="${file%%.txt*}"
        else
            file_base="${file%%_n-*.root*}"
        fi
        
        classified_files["$file_base"]="${classified_files["$file_base"]} $prefix$file"
    done
    
    for file_base in ${!classified_files[@]}; do
        echo Generating outputList/"$output_prefix"_"$file_base".txt
        
        echo "${classified_files[$file_base]}" | sed 's/^ *//' | tr ' ' '\n' > outputList/"$output_prefix"_"$file_base".txt
    done
}
classify_files "/store/user/xinlong/XHY4bRun3_skim" "SKIM" 
classify_files "/store/user/xinlong/XHY4bRun3_selection_1p1" "SELECTION" 
classify_files "/store/user/xinlong/XHY4bRun3_division_1p1" "DIVISION" 
