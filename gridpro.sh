work=$1
if [[ $work == skim ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_skim/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi


if [[ $work == selection_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_1p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_1p1_args.txt -i "cpp_modules run_selection_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == Nminus1_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_Nminus1_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_Nminus1_1p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a Nminus1_1p1_args.txt -i "cpp_modules run_Nminus1_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi


if [[ $work == division_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_division_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_division_1p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a division_1p1_args.txt -i "cpp_modules run_division_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == selection_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_selection_2p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_2p1_args.txt -i "cpp_modules run_selection_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == Nminus1_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_Nminus1_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_Nminus1_2p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a Nminus1_2p1_args.txt -i "cpp_modules run_Nminus1_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi


if [[ $work == division_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_division_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_division_2p1/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a division_2p1_args.txt -i "cpp_modules run_division_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi


if [[ $work == skim_a ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/tmp/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a amend_skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi
if [[ $work == skim_amend ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_skim/#g' gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a amend_skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi
