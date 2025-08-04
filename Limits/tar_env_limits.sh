# capture current dir
WD=$(pwd)
cd $CMSSW_BASE/../
tar --exclude-vcs --exclude-caches-all -cvzf tar_2dalphabet.tgz \
    --exclude=tmp --exclude=".scram" --exclude=".SCRAM" \
    CMSSW_14_1_0_pre4

xrdcp -f tar_2dalphabet.tgz root://cmseos.fnal.gov//store/user/$USER/tar_2dalphabet.tgz
cd ${WD}
