work=$1
if [[ $work == skim ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_skim/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi


if [[ $work == selection_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_1p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_args.txt -i "cpp_modules run_selection_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == Nminus1_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_Nminus1_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_Nminus1_1p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a Nminus1_args.txt -i "cpp_modules run_Nminus1_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi


if [[ $work == division_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_division_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_division_1p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a division_1p1_args.txt -i "cpp_modules run_division_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == selection_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_2p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_args.txt -i "cpp_modules run_selection_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == Nminus1_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_Nminus1_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_Nminus1_2p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a Nminus1_args.txt -i "cpp_modules run_Nminus1_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi


if [[ $work == division_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_division_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_division_2p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a division_2p1_args.txt -i "cpp_modules run_division_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == selection_compound ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_compound.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_compound/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_args.txt -i "cpp_modules run_selection_compound.py XHY4b_Analyzer.py raw_nano outputList"
fi
















if [[ $work == skim_a ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/tmp/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a amend_skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi
if [[ $work == skim_amend ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_skim/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a amend_skim_args.txt -i "run_skim.py XHY4b_Analyzer.py raw_nano cpp_modules outputList"
fi
if [[ $work == selection_2p1_debug ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_2p1_debug.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_2p1_debug/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_2p1_debug_args.txt -i "cpp_modules run_selection_2p1_debug.py XHY4b_Analyzer.py raw_nano outputList"
fi
if [[ $work == mass_debug_2p1 ]] ; then
    
    sed -e 's/PYTHON_SCRIPT/run_mass_debug_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_mass_debug_2p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a mass_debug_2p1_args.txt -i "cpp_modules run_mass_debug_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == selection_1p1_debug ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_1p1_debug.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_1p1_debug/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_1p1_debug_args.txt -i "cpp_modules run_selection_1p1_debug.py XHY4b_Analyzer.py raw_nano outputList"
fi

if [[ $work == trigger_1p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_without_trigger_1p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_without_trigger_1p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_args.txt -i "cpp_modules run_selection_without_trigger_1p1.py XHY4b_Analyzer.py raw_nano outputList"
fi
if [[ $work == trigger_2p1 ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_selection_without_trigger_2p1.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/XHY4bRun3_selection_without_trigger_2p1/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a selection_args.txt -i "cpp_modules run_selection_without_trigger_2p1.py XHY4b_Analyzer.py raw_nano outputList"
fi
