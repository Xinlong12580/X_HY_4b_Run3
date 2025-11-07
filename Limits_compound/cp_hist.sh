mkdir -p Templates
input_dir="/store/user/xinlong/XHY4bRun3_2022_division_1p1"
files=$( eosls $input_dir )
prefix=$eosprefix$input_dir/
for file in $files; do
    if [[ $file == *"Templates"*  ]]; then
        xrdcp $prefix/$file Templates
    fi
done
