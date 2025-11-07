#make json files 
mode=$1
if [[ X$mode == X ]]; then
    echo "Must specify mode (1p1 or 2p1)" >&2
    exit 1
fi
sed -e "s/R_PASS/SR1/g" -e "s/R_FAIL/SB1/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_SR1_SB1.json
sed -e "s/R_PASS/SR2/g" -e "s/R_FAIL/SB2/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_SR2_SB2.json
sed -e "s/R_PASS/VS2/g" -e "s/R_FAIL/VB1/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_VS2_VB1.json
sed -e "s/R_PASS/VS1/g" -e "s/R_FAIL/VB1/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_VS1_VB1.json
sed -e "s/R_PASS/VS4/g" -e "s/R_FAIL/VB2/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_VS4_VB2.json
sed -e "s/R_PASS/VS3/g" -e "s/R_FAIL/VB2/g" -e "s/MODE/$mode/g" -e "s/MBINS/B_$mode/g" XYH.json > XYH_VS3_VB2.json
