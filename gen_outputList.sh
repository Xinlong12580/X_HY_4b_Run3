rm outputList/*
mkdir -p outputList

#collect all output root files belonging to the same dataset
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
        if [[ $output_prefix == *DIVISION* &&  $file != *"SR1"*"nom"*"2022EE"*"Signal"* ]]; then
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
classify_files "/store/user/$USER/XHY4bRun3_skim" "SKIM" 
#classify_files "/store/user/$USER/XHY4bRun3_selection_1p1" "SELECTION_1P1" 
#classify_files "/store/user/$USER/XHY4bRun3_division_1p1" "DIVISION_1P1" 
#classify_files "/store/user/$USER/XHY4bRun3_selection_2p1" "SELECTION_2P1" 
#classify_files "/store/user/$USER/XHY4bRun3_selection_2p1" "SELECTION_2P1" 
#classify_files "/store/user/$USER/XHY4bRun3_division_2p1" "DIVISION_2P1" 




#collecting all output files
skim_dir=/store/user/$USER/XHY4bRun3_skim/
eosls $skim_dir > outputList/output_skim_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$skim_dir@" outputList/output_skim_tmp.txt > outputList/output_skim.txt

skim_1_dir=/store/user/$USER/XHY4bRun3_skim_1_tmp/
eosls $skim_dir > outputList/output_skim_1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$skim_1_dir@" outputList/output_skim_1_tmp.txt > outputList/output_skim_1.txt

selection_dir=/store/user/$USER/XHY4bRun3_selection_1p1/
eosls $selection_dir"nom*" > outputList/output_selection_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$selection_dir@" outputList/output_selection_tmp.txt > outputList/output_selection_1p1.txt

Nminus1_dir=/store/user/$USER/XHY4bRun3_Nminus1_1p1/
eosls $Nminus1_dir"nom*" > outputList/output_Nminus1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$Nminus1_dir@" outputList/output_Nminus1_tmp.txt > outputList/output_Nminus1_1p1.txt

Nminus1_2p1_dir=/store/user/$USER/XHY4bRun3_Nminus1_2p1/
eosls $Nminus1_2p1_dir"nom*" > outputList/output_Nminus1_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$Nminus1_2p1_dir@" outputList/output_Nminus1_2p1_tmp.txt > outputList/output_Nminus1_2p1.txt

selection_2p1_dir=/store/user/$USER/XHY4bRun3_selection_2p1/
eosls $selection_2p1_dir > outputList/output_selection_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$selection_2p1_dir@" outputList/output_selection_2p1_tmp.txt > outputList/output_selection_2p1.txt

selection_2p1_dir=/store/user/$USER/XHY4bRun3_selection_2p1_debug/
eosls $selection_2p1_dir > outputList/output_selection_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$selection_2p1_dir@" outputList/output_selection_2p1_tmp.txt > outputList/output_selection_2p1_debug.txt


division_1p1_dir=/store/user/$USER/XHY4bRun3_division_1p1/
eosls $division_1p1_dir  > outputList/output_division_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$division_1p1_dir@" outputList/output_division_tmp.txt > outputList/output_division_1p1.txt


division_2p1_dir=/store/user/$USER/XHY4bRun3_division_2p1/
eosls $division_2p1_dir > outputList/output_division_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$division_2p1_dir@" outputList/output_division_2p1_tmp.txt > outputList/output_division_2p1.txt


file_dir=/store/user/$USER/XHY4bRun3_mass_debug_2p1/
eosls $file_dir > outputList/output_mass_debug_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$file_dir@" outputList/output_mass_debug_2p1_tmp.txt > outputList/output_mass_debug_2p1.txt


rm outputList/*tmp*
