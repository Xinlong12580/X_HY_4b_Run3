MX=$1
MY=$2
MX=3000
MY=300

python XYH.py --tf 1x1 --sig $MX-$MY --r_fail SB2 --r_pass SR2 --make --makeCard --wsp SR1w_MX-"$MX"_MY-"$MY"
./run_blinded.sh --fitdir SR1w_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -bl -v 3
