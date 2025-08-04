mode=$1
if [[ X$mode == X ]]; then
    mode=1p1
fi
sed -e "s/R_PASS/SR1/g" -e "s/R_FAIL/SB1/g" -e "s/MODE/$mode/g" XYH.json > XYH_SR1_SB1.json
sed -e "s/R_PASS/SR2/g" -e "s/R_FAIL/SB2/g" -e "s/MODE/$mode/g" XYH.json > XYH_SR2_SB2.json
sed -e "s/R_PASS/VS2/g" -e "s/R_FAIL/VB1/g" -e "s/MODE/$mode/g" XYH.json > XYH_VS2_VB1.json
