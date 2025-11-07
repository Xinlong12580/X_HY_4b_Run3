#!/bin/bash
root_dir=$(pwd)
OUTTXT="$1"_"$2"_"$3"_"$4"_"${5}"_"${6}"_output.log
OUTTXT="${OUTTXT//\//_}"
echo "OUTTXT" $OUTTXT
echo "Run script starting" | tee $root_dir/$OUTTXT
echo "Running on: `uname -a`" | tee -a $root_dir/$OUTTXT
echo "System software: `cat /etc/redhat-release`" | tee -a $root_dir/$OUTTXT

# Set up pre-compiled CMSSW env
ls | tee -a $root_dir/$OUTTXT
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/xinlong/tar_2dalphabet.tgz ./
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW CMSSW_14_1_0_pre4
echo "Unpacking compiled CMSSW environment tarball..." | tee -a $root_dir/$OUTTXT
tar -xzvf tar_2dalphabet.tgz | tee -a $root_dir/$OUTTXT
rm tar_2dalphabet.tgz
mkdir tardir 
cp tarball.tgz tardir/ 
cd tardir/
tar -xzvf tarball.tgz | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
rm tarball.tgz
mkdir ../CMSSW_14_1_0_pre4/src/testdir
cp -r * ../CMSSW_14_1_0_pre4/src/testdir
cd ../CMSSW_14_1_0_pre4/src/
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
echo "CECK0" | tee -a $root_dir/$OUTTXT
cmsenv 2>&1 | tee -a $root_dir/$OUTTXT
echo $CMSSW_BASE | tee -a $root_dir/$OUTTXT
echo "CECK0" | tee -a $root_dir/$OUTTXT
 
# CMSREL and virtual env setup
echo 'IN RELEASE' | tee -a $root_dir/$OUTTXT
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
echo 'scramv1 runtime -sh' | tee -a $root_dir/$OUTTXT
eval `scramv1 runtime -sh` | tee -a $root_dir/$OUTTXT
echo $CMSSW_BASE "is the CMSSW we have on the local worker node" | tee -a $root_dir/$OUTTXT
echo 'python3 -m venv timber-env' | tee -a $root_dir/$OUTTXT
python3 -m venv twoD-env
echo 'source twoD-env/bin/activate' | tee -a $root_dir/$OUTTXT
source twoD-env/bin/activate
ls twoD-env | tee -a $root_dir/$OUTTXT
echo "$(which python3)" | tee -a $root_dir/$OUTTXT

# Set up TIMBER
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/el8_amd64_gcc10/external/boost/1.78.0-0d68c45b1e2660f9d21f29f6d0dbe0a0/lib
export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$(correction config --incdir)
cd testdir
pwd | tee -a $root_dir/$OUTTXT

# xrootd debug & certs
#export XRD_LOGLEVEL=Debug
export X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates/

# MAIN FUNCTION
MX=$1
MY=$2
R_FAIL=$3
R_PASS=$4
python XYH.py --tf 1x1 --sig $MX-$MY --r_fail $R_FAIL --r_pass $R_PASS --make --makeCard --wsp "$R_PASS"w_MX-"$MX"_MY-"$MY"
./run_blinded.sh --fitdir "$R_PASS"w_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -bl -v 3
status=${PIPESTATUS[0]}
if [ $status -eq 0 ]; then
    # move all snapshots to the EOS (there will only be one)
    tar -xzvf *workspace
    xrdcp -f *tar root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_limits_1p1/
else
    mv $root_dir/$OUTTXT $root_dir/FAILED_$OUTTXT
    OUTTXT=FAILED_$OUTTXT
fi
ls | tee -a $root_dir/$OUTTXT
xrdcp -f $root_dir/$OUTTXT root://cmseos.fnal.gov//store/user/xinlong/XHY4bRun3_limits_1p1/
