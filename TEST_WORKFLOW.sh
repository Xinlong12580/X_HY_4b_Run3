python run_skim.py -d raw_nano/files/2022EE__Data__JetMET__Run2022E-22Sep2023-v1__NANOAOD.txt -y 2022EE -n 2 -i 0
mv masked_skimmed_2022EE__Data__JetMET__Run2022E-22Sep2023-v1__NANOAOD.txt_n-2_i-0.root TEST_SKIM.root
python run_selection.py -d TEST_SKIM.root -y 2022EE -n 2 -i 0
python run_division.py -d tagged_selected_TEST_SKIM.root -y 2022EE -n 2 -i 0 -r VS2
