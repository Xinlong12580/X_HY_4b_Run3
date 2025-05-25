mkdir -p outputList
classify_files(){
    input_dir=$1
    output_prefix=$2
    files=$( eosls $input_dir )
    prefix=$eosprefix$input_dir/
    declare -A classified_files
    for file in ${files[@]}; do
        file_base="${file%%.txt*}"
        classified_files["$file_base"]="${classified_files["$file_base"]} $prefix$file"
    done
    
    for file_base in ${!classified_files[@]}; do
        echo Generating outputList/"$output_prefix"_"$file_base".txt
        
        echo "${classified_files[$file_base]}" | sed 's/^ *//' | tr ' ' '\n' > outputList/"$output_prefix"_"$file_base".txt
    done
}
classify_files "/store/user/xinlong/XHY4bRun3_2022_skim" "SKIM" 
classify_files "/store/user/xinlong/XHY4bRun3_2022_selection2_1p1" "SELECTION" 
classify_files "/store/user/xinlong/XHY4bRun3_2022_division" "DIVISION" 
