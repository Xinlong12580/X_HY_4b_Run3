while getopts "y:d:" opt; do
  case $opt in
    y) year="$OPTARG" ;;
    d) dataset="$OPTARG" ;;
    *) echo "Usage: $0 -y year -d dataset" >&2; exit 1 ;;
  esac
done
echo $year $dataset
json_file=datasets_XHY4b.json
if [ $dataset = "SignalMC_XHY4b" ]; then
    json_file=signal_XHY4b.json
fi
readarray -t files < <(jq -r .\"$year\".\"$dataset\"[] $json_file)
> bad_dataset_"$year"_"$dataset".txt
for file in ${files[@]}; do
    echo TRYING TO GET DATASET: $file
	Command="file dataset="$file
	data_name=./files/"$year"_"$dataset""${file//\//_}"
	#echo $Command
	#echo dasgoclient -query "$Command"
	#dasgoclient -query "$Command" | tee "$data_name"_tmp.txt
	dasgoclient -query "$Command" > "$data_name"_tmp.txt
    statusflag=$(tail -c 26 "$data_name"_tmp.txt)
    if [ "$statusflag" = "unmatched dataset pattern" ]; then
	    echo "$data_name" >> bad_dataset.txt
        echo "\e[31mGETTING $file FAILED.\e[0m" 
    else
        sed 's@^@root://cmsxrootd.fnal.gov/@' "$data_name"_tmp.txt > "$data_name".txt
        echo -e "\e[32mGETTING $file SUCCESSFUL.\e[0m" 
	fi
    rm "$data_name"_tmp.txt
done
echo BAD DATASET OF  "$year" "$dataset":
cat bad_dataset_"$year"_"$dataset".txt
