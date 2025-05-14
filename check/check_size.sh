dir_name=/store/user/xinlong/XHY4bRun3_2022_skim/
files=$(eosls "$dir_name"*QCD*)
total=0
for file in ${files[@]}; do 
    filesize=$(eosls -l $dir_name$file | awk '{print $5}')
    filesize=$((filesize / 1024 / 1024))
    total=$((total + filesize))
    echo "File size: $filesize MB"
done
echo "Total File size: $total MB"
