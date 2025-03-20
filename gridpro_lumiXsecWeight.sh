#python CondorHelper.py -r run_snapshot.sh -a snapshot_args.txt -i "snapshot.py"
python CondorHelper.py -r gridrun_lumiXsecWeight.sh -a lumiXsecWeight_args.txt -i "lumiXsecWeight.cc run_lumiXsecWeight.py XHY4b_Analyzer.py raw_nano columnBlackList.txt"
