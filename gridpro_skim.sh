#python CondorHelper.py -r run_snapshot.sh -a snapshot_args.txt -i "snapshot.py"
python CondorHelper.py -r gridrun_skim.sh -a skim_args.txt -i "deltaRMatching.cc helperFunctions.cc run_skim.py XHY4b_Analyzer.py raw_nano columnBlackList.txt"
