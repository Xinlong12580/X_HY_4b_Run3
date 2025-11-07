MX=$1
MY=$2
MX=3000
MY=1000

python XYH.py --tf 1x1 --sig $MX-$MY --r_fail VB1 --r_pass VS2 --make --makeCard --wsp Control_diagnostics_MX-"$MX"_MY-"$MY" --fit --plot
#python XYH.py --tf 1x1 --sig $MX-$MY --r_fail VB1 --r_pass VS2 --wsp Control_diagnostics_MX-"$MX"_MY-"$MY" --plot
./run_fit.sh  --fitdir Control_diagnostics_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -b -v 3 
