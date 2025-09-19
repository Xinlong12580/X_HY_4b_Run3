division_1p1_dir=/store/user/$USER/XHY4bRun3_division_1p1/
eosls $division_1p1_dir  > outputList/output_division_1p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$division_1p1_dir@" outputList/output_division_1p1_tmp.txt > outputList/output_division_1p1.txt


division_2p1_dir=/store/user/$USER/XHY4bRun3_division_2p1/
eosls $division_2p1_dir > outputList/output_division_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$division_2p1_dir@" outputList/output_division_2p1_tmp.txt > outputList/output_division_2p1.txt


dir=/store/user/$USER/XHY4bRun3_limits_1p1/
eosls $dir > outputList/output_limits_1p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$dir@" outputList/output_limits_1p1_tmp.txt > outputList/output_limits_1p1.txt

dir=/store/user/$USER/XHY4bRun3_limits_2p1/
eosls $dir > outputList/output_limits_2p1_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$dir@" outputList/output_limits_2p1_tmp.txt > outputList/output_limits_2p1.txt

rm outputList/*tmp*
