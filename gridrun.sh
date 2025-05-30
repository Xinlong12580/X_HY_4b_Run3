#!/bin/bash
root_dir=$(pwd)
echo "Run script starting" | tee $root_dir/out.txt
echo "Running on: `uname -a`" | tee -a $root_dir/out.txt
echo "System software: `cat /etc/redhat-release`" | tee -a $root_dir/out.txt

# Set up pre-compiled CMSSW env
ls | tee -a $root_dir/out.txt
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/xinlong/testtar.tgz ./
export SCRAM_ARCH=el8_amd64_gcc10
scramv1 project CMSSW CMSSW_12_3_5
echo "Unpacking compiled CMSSW environment tarball..." | tee -a $root_dir/out.txt
tar -xzvf testtar.tgz | tee -a $root_dir/out.txt
tar -xzvf tarcmssw.tgz | tee -a $root_dir/out.txt
tar -xzvf tartimber.tgz | tee -a $root_dir/out.txt
rm testtar.tgz
rm tarcmssw.tgz
rm tartimber.tgz
mkdir tardir 
cp tarball.tgz tardir/ 
cd tardir/
tar -xzvf tarball.tgz | tee -a $root_dir/out.txt
ls | tee -a $root_dir/out.txt
rm tarball.tgz
mkdir ../CMSSW_12_3_5/src/testdir
cp -r * ../CMSSW_12_3_5/src/testdir
cd ../CMSSW_12_3_5/src/

# CMSREL and virtual env setup
echo 'IN RELEASE' | tee -a $root_dir/out.txt
pwd | tee -a $root_dir/out.txt
ls | tee -a $root_dir/out.txt
echo 'scramv1 runtime -sh' | tee -a $root_dir/out.txt
eval `scramv1 runtime -sh`
echo $CMSSW_BASE "is the CMSSW we have on the local worker node" | tee -a $root_dir/out.txt
echo 'python3 -m venv timber-env' | tee -a $root_dir/out.txt
python3 -m venv timber-env
echo 'source timber-env/bin/activate' | tee -a $root_dir/out.txt
source timber-env/bin/activate
echo "$(which python3)" | tee -a $root_dir/out.txt

# Set up TIMBER
cd ../..
pwd | tee -a $root_dir/out.txt
ls | tee -a $root_dir/out.txt
echo "CP0" | tee -a $root_dir/out.txt
ls TIMBER  | tee -a $root_dir/out.txt
cd TIMBER 
echo "CP1" | tee -a $root_dir/out.txt
pwd | tee -a $root_dir/out.txt
ls | tee -a $root_dir/out.txt
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/el8_amd64_gcc10/external/boost/1.78.0-0d68c45b1e2660f9d21f29f6d0dbe0a0/lib
export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$(correction config --incdir)
echo "STARTING TIMBER SETUP......." | tee -a $root_dir/out.txt
source setup.sh
echo "FINISHED TIMBER SETUP......." | tee -a $root_dir/out.txt
cd ../CMSSW_12_3_5/src/testdir
pwd | tee -a $root_dir/out.txt

# xrootd debug & certs
#export XRD_LOGLEVEL=Debug
export X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates/

# MAIN FUNCTION
echo python run_division_1p1.py $* | tee -a $root_dir/out.txt
python run_division_1p1.py $* | tee -a $root_dir/out.txt
ls | tee -a $root_dir/out.txt
# move all snapshots to the EOS (there will only be one)
xrdcp -f *.root root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_2022_division_1p1/
xrdcp -f $root_dir/out.txt root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_2022_division_1p1/
