#python CondorHelper.py -r run_snapshot.sh -a snapshot_args.txt -i "snapshot.py"
python CondorHelper.py -r gridrun_selection.sh -a selection_args.txt -i "massMatching.cc Matching.cc helperFunctions.cc deltaRMatching.cc run_selection.py XHY4b_Analyzer.py raw_nano columnBlackList.txt"

