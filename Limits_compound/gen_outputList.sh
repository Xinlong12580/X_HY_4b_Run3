
file_dir=/store/user/$USER/XHY4bRun3_division_compound/
eosls $file_dir > outputList/output_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$file_dir@" outputList/output_tmp.txt > outputList/output_division_compound.txt
rm outputList/*tmp*
