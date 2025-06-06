skim_dir=/store/user/xinlong/XHY4bRun3_skim/
eosls $skim_dir > outputList/output_skim_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$skim_dir@" outputList/output_skim_tmp.txt > outputList/output_skim.txt

skim_1_dir=/store/user/xinlong/XHY4bRun3_skim_1_tmp/
eosls $skim_dir > outputList/output_skim_1_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$skim_1_dir@" outputList/output_skim_1_tmp.txt > outputList/output_skim_1.txt

selection_dir=/store/user/xinlong/XHY4bRun3_selection_1p1/
eosls $selection_dir"nom*" > outputList/output_selection_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$selection_dir@" outputList/output_selection_tmp.txt > outputList/output_selection.txt

Nminus1_dir=/store/user/xinlong/XHY4bRun3_Nminus1_1p1/
eosls $Nminus1_dir"nom*" > outputList/output_Nminus1_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$Nminus1_dir@" outputList/output_Nminus1_tmp.txt > outputList/output_Nminus1_1p1.txt

selection_2p1_dir=/store/user/xinlong/XHY4bRun3_selection2_2p1_hadded/
eosls $selection_2p1_dir > outputList/output_selection_2p1_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$selection_2p1_dir@" outputList/output_selection_2p1_tmp.txt > outputList/output_selection_2p1.txt



division_dir=/store/user/xinlong/XHY4bRun3_selection_1p1_hadded/
eosls $division_dir | grep "_tagged" > outputList/output_division_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$division_dir@" outputList/output_division_tmp.txt > outputList/output_division.txt


division_2p1_dir=/store/user/xinlong/XHY4bRun3_division_2p1/
eosls $division_2p1_dir > outputList/output_division_2p1_tmp.txt
sed "s@^@root://cmsxrootd.fnal.gov/$division_2p1_dir@" outputList/output_division_2p1_tmp.txt > outputList/output_division_2p1.txt




rm outputList/*tmp*
