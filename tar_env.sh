# capture current dir
WD=$(pwd)
cd $CMSSW_BASE/../
tar --exclude-vcs --exclude-caches-all -cvzf tarcmssw.tgz \
    --exclude=tmp --exclude=".scram" --exclude=".SCRAM" \
    --exclude=CMSSW_12_3_5/src/timber-env \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/logs \
    --exclude=CMSSW_12_3_5/src/TIMBER/docs \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/plots \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/rootfiles/*.root \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/trijet_nano/PFnano_backup \
    --exclude=CMSSW_12_3_5/src/TIMBER/TIMBER/data/JE*/backup_* \
    --exclude=CMSSW_12_3_5/src/TIMBER/bin/libtimber_* \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/triggers/backup_* \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/raw_nano/backup* \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/raw_nano/private* \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/ParticleNetSFs/EfficiencyMaps/*.root \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/HWWsnapshot*.root \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/rootfiles/old* \
    --exclude=CMSSW_12_3_5/src/TIMBER/TIMBER/data_* \
    --exclude=CMSSW_12_3_5/src/XHYbbWW/logs \
    CMSSW_12_3_5
cd $TIMBERPATH/../
tar -cvzf tartimber.tgz TIMBER
tar -cvzf testtar.tgz tartimber.tgz tarcmssw.tgz

xrdcp -f testtar.tgz root://cmseos.fnal.gov//store/user/$USER/testtar.tgz
cd ${WD}
