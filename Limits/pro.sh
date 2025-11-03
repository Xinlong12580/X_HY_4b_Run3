MX=$1
MY=$2
MX=3000
MY=1000

python XYH.py --tf 1x1 --sig $MX-$MY --r_fail VB1 --r_pass VS2 --make --makeCard --wsp Control_MX-"$MX"_MY-"$MY"
#python XYH.py --tf 1x1 --sig $MX-$MY --r_fail SB2 --r_pass SR2 --make --makeCard --wsp Loose_MX-"$MX"_MY-"$MY"

./run_fit.sh  --fitdir Control_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -b -v 3 
#./run_fit_diagnostics.sh --fitdir Control_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -b -v 3 

status=${PIPESTATUS[0]}
echo $status
control_file=Control_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/higgsCombineSnapshot.MultiDimFit.mH125.root
control_file=Control_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/higgsCombineSnapshot.MultiDimFit.mH125.root
root -b -q load_parameters.C\(\"$control_file\"\)

#./run_limits.sh --fitdir Loose_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -l -v 2
