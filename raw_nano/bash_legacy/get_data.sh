files=("/JetHT/Run2022C-22Sep2023-v1/NANOAOD" \
	"/JetMET/Run2022C-22Sep2023-v1/NANOAOD" \
	"/JetMET/Run2022D-22Sep2023-v1/NANOAOD" \
	"/JetMET/Run2022E-22Sep2023-v1/NANOAOD" \
	"/JetMET/Run2022F-22Sep2023-v2/NANOAOD" \
	"/JetMET/Run2022G-22Sep2023-v2/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v4-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v4-v1/NANOAOD" \
	"/JetMET0/Run2023D-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET1/Run2023D-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET0/Run2023D-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET1/Run2023D-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v1-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v2-v1/NANOAOD" \
	"/JetMET0/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/JetMET1/Run2023C-22Sep2023_v3-v1/NANOAOD" \
	"/ParkingHH/Run2023C-22Sep2023_v4-v1/NANOAOD" \
	"/ParkingHH/Run2023D-22Sep2023_v1-v1/NANOAOD" \
	"/ParkingHH/Run2023D-22Sep2023_v2-v1/NANOAOD")
for file in ${files[@]}; do
	Command="file dataset="$file
	data_name=Data"${file//\//_}"
	echo $Command
	echo dasgoclient -query "$Command"
	dasgoclient -query "$Command" | tee "$data_name"_tmp.txt
	sed 's@^@root://cmsxrootd.fnal.gov/@' "$data_name"_tmp.txt > "$data_name".txt
	rm "$data_name"_tmp.txt
done
