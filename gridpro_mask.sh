#python CondorHelper.py -r run_snapshot.sh -a snapshot_args.txt -i "snapshot.py"
python CondorHelper.py -r gridrun_mask.sh -a mask_args.txt -i "goldenJson_mask.cc run_mask.py XHY4b_Analyzer.py raw_nano columnBlackList.txt"
