MX=$1
MY=$2
R_FAIL=$3
R_PASS=$4
mode=$5
./load_fit.sh $MX $MY $mode
./make_json.sh $mode
python3 XYH.py --tf 1x1 --sig $MX-$MY --r_fail $R_FAIL --r_pass $R_PASS --make --makeCard --wsp "$R_PASS"w_MX-"$MX"_MY-"$MY"
./run_blinded.sh --fitdir "$R_PASS"w_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -bl -v 3
