rm *root
#eosrm /store/user/xinlong/XHY4bRun3_2022_selection2_hadded/*
files=$( eosls /store/user/xinlong/XHY4bRun3_2022_selection2_tmp/ )
prefix=$eosprefix/store/user/xinlong/XHY4bRun3_2022_selection2_tmp/
declare -A classified_files
declare -A classified_file_idxs
for file in ${files[@]}; do
    file_base="${file%%_n-*}"
    classified_files["$file_base"]="${classified_files["$file_base"]} $prefix$file"
    tmp="${file#*_i-}"
    file_idx="${tmp%%.root*}"
    #classfified_file_idxs["$file_base"]="${classfified_file_idxs["$file_base"]} $file_idx"
done

for file_base in ${!classified_files[@]}; do
    echo $file_base
    echo ${classified_files[$file_base]}
    hadd "$file_base"_ALL.root ${classified_files[$file_base]}
    xrdcp -f "$file_base"_ALL.root root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_2022_selection2_hadded/
done


