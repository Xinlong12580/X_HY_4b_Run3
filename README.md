# Quick Start
## Prerequisite
This repo assumes *TIMBER* and *2DAlphabet* are already installed. For compatibility, please use this [TIMBER](https://github.com/Xinlong12580/TIMBER/tree/Run3_update) branch and this [2DAlphabet](https://github.com/JHU-Tools/2DAlphabet) branch. In most cases the installation location of the packages doesn't matter, and you can follow the instructions on the package repo page to install them. However, if you want to use the `tar_env_2DA.sh` and `tar_env_TIMBER.sh` script to create enviroment setting for you GRID jobs, or use `set_env_2DA.sh` and `set_env_TIMBER.sh` to set local enviroment, please follow the instructions below to install them correctly.

For *TIMBER*, log into lpc8 and run:
```
cd \your\working\directory
mkdir Env_TIMBER
cd Env_TIMBER
cmsrel CMSSW_12_3_5
cd CMSSW_12_3_5
cmsenv
cd ..
python3 -m virtualenv timber-env
git clone https://github.com/Xinlong12580/TIMBER.git -b Run3_update
cd TIMBER/
mkdir bin
cd bin
git clone git@github.com:fmtlib/fmt.git
cd ../..
```
Then you create a file `tmp1.sh` with these lines:
```
cat <<EOT >> timber-env/bin/activate

export BOOSTPATH=/cvmfs/cms.cern.ch/el8_amd64_gcc10/external/boost/1.78.0-0d68c45b1e2660f9d21f29f6d0dbe0a0/lib
if grep -q '\${BOOSTPATH}' <<< '\${LD_LIBRARY_PATH}'
then
  echo 'BOOSTPATH already on LD_LIBRARY_PATH'
else
  export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}:\${BOOSTPATH}
  echo 'BOOSTPATH added to PATH'
fi

if [[ "\${CMSSW_BASE}" ]]; then
    export ROOT_INCLUDE_PATH=\$ROOT_INCLUDE_PATH:\$(correction config --incdir)
    echo 'correctionlib libraries added to ROOT_INCLUDE_PATH'
fi

EOT
```
and run:
```
source tmp1.sh
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ..
```
then you create another file `tmp2.sh` with these lines:
```
{ cat <<EOT; cat timber-env/bin/activate; } > temp && mv temp timber-env/bin/activate
curr_dir=\$(pwd)
source_dir=\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)
cd \$source_dir/../../CMSSW_12_3_5
cmsenv
cd \$curr_dir
EOT
```
and run
```
source tmp2.sh
```

For 2DAphaBet, you need to log out lpc8 and log into lpc9. Then:
```
cd /your/working/directory #The same as last one
mkdir Env_2DAlphabet
cd Env_2DAlphabet
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.0.1
cd ../../
git clone --branch CMSWW_14_1_0_pre4 git@github.com:JHU-Tools/CombineHarvester.git
scramv1 b clean
scramv1 b -j 16
git clone git@github.com:JHU-Tools/2DAlphabet.git
python3 -m virtualenv twoD-env
source twoD-env/bin/activate
cd 2DAlphabet/
python3 setup.py develop
cd ..
```
Then you make a file `tmp1.sh` with these lines:
```
{ cat <<EOT; cat twoD-env/bin/activate; } > temp && mv temp twoD-env/bin/activate
curr_dir=\$(pwd)
source_dir=\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)
cd \$source_dir/../../
cmsenv
cd \$curr_dir
EOT
```
and run
```
source tmp1.sh
```

## Running Selection

### Enviroment Setup
#### Local Env
If you want to use `set_Env_TIMBER.sh` and `set_Env_2DA.sh`, make sure you clone the analysis repo to the same working directory:
```
cd /your/working/directory #same as above
git clone https://github.com/Xinlong12580/X_HY_4b_Run3.git
```
For the instructions below we assume you installed all the packages to the locations above.

To run selection locally, we need to use the *TIMBER* enviroment. Log into lpc8 and use `set_env_TIMBER.sh` to set the enviroment:
```
cd /your/working/directory/X_HY_4b_Run3
source set_Env_TIMBER.sh
```
#### GRID Env
To run selection on GRID, we need to create a tarball of TIMBER environment and send it to eos. Run
```
tar_env_TIMBER.sh
```
you can run `eosls /store/user/$USER/` and check if `tarTIMBER.tgz` is created. 

Also, create a directory to store some logs:
```
mkdir logs
```
### Overview
The selection procedure is divided into three steps:
- Running skimming on the raw files. 1+1 channel and 2+1 channel share the same skims. The script for this step is `run_skim.py`
- Running selection for 1+1 and 2+1 channel separately. The script for this step is `run_selection_1p1.py` and `run_selection_2p1.py` for 1+1 and 2+2 channel, respectively.
- Dividing the events in the output of the selection step into different regions based on b-tagging scores. The script for this step is `run_division_1p1.py` and `run_division_2p1.py` for 1+1 and 2+2 channel, respectively.

The output file of each step is the input of the next step. If we are running jobs on GRID, generally we will have lots of files created and they need to be fed into the next step. the script `gen_outputList.sh` will fetch the names of these files and orgnize them, and the script `gen_args_pro.sh` will generate the input arguments for the next step
### skim
#### Local Job
To run skimming, generate the arguments using `gen_args_pro.sh`:
```
./gen_args.pro.sh skim
```
you will see a file called `skim_args.txt` created. open this file and copy a line, then you can use `run_skim.py` to run skim on it. For example:
```
python3 run_skim.py -d raw_nano/files/2023__SignalMC_XHY4b__MX-900_MY-60.txt -y 2023 -n 2 -i 0
```
You will see a file called `skimmed_2023__SignalMC_XHY4b__MX-900_MY-60.txt_n-1_i-0.root` generated, which contains the snapshot after skimming.

#### GRID Job
The outfile files will be stored under `/store/user/$USER/XHY4bRun3_skim/` on eos. Note this directory will NOT be created automatically, so please create it manually before running jobs:
```
eosmkdir /store/user/$USER/XHY4bRun3_skim/
```
then create the input arguments using `gen_args_pro.sh`:
```
./gen_args.pro.sh skim
```

then submit the jobs using `gridpro.sh`:
```
./gridpro.sh
```
### main selection
Assuming if you've already run some skim jobs on GRID. Then create a directory `outputList` and use `gen_outputList.sh` to collect the outputs. open `gen_outputList.sh` and uncomment this line:
```
classify_files "/store/user/$USER/XHY4bRun3_skim" "SKIM"
```
then run:
```
mkdir outputList
./gen_outputList.sh
```
then you will see the output files under `outputList`.

Then we create the arguments for 1+1 and 2+1 selection using `gen_args_pro.sh`. Run
```
./gen_args_pro.sh selection_1p1 skim
./gen_args_pro.sh selection_2p1 skim
```
you should see two files `selection_1p1_args.txt` and `selection_2p1_args.txt` generated. You can copy a line from `selection_1p1_args.txt` and run `run_selection_1p1.py` locally, or copy a line from `selection_2p1_args.txt` and run `run_selection_2p1.py`. For example:
```
 python3 run_selection_1p1.py -d outputList/SKIM_skimmed_2023__SignalMC_XHY4b__MX-900_MY-60.txt -y 2023 -n 1 -i 0 -s nom
```
You will see two files produced. One is `nom_tagged_selected_SKIM_skimmed_2023__SignalMC_XHY4b__MX-900_MY-60_n-1_i-0.root`, containing the snapshot of the selection flow; another one is `Templates_nom_tagged_selected_SKIM_skimmed_2023__SignalMC_XHY4b__MX-900_MY-60_n-1_i-0.root`, which contains some Templates in it. Note you can also change the argument after `-d ` to a local `.root` file.

To run it on GRID, run
```
eosmkdir /store/user/$USER/XHY4bRun3_selection_1p1/
./gridpro.sh selection_1p1
```
for 1+1 channel and
```
eosmkdir /store/user/$USER/XHY4bRun3_selection_2p1/
./gridpro.sh selection_2p1
```
for 2+1 channel.
### division
to run division for 1+1 channel, we generate the output of 1+1 main selection first. Uncomment this line in gen_outputList.sh:
```
#classify_files "/store/user/$USER/XHY4bRun3_selection_1p1" "SELECTION_1P1"
```
and run:
```
./gen_outputList.sh 
```
Then we can generate the input args:
```
./gen_args_pro.sh division_1p1 selection_1p1
```
you will see a file called `division_1p1_args.txt` created. Copy a line and run it locally with `run_division_1p1.py`, for example:
```
 python3 run_division_1p1.py -d outputList/SELECTION_1P1_JER__down_tagged_selected_SKIM_skimmed_20
22EE__MC_DibosonJets__WWto4Q.txt -y 2022EE -n 10000 -i 0
```
You will see 20 output files, where 10 of them contain the snapshots of 10 regions and another 10 of them contain the 2D templates of 10 regions that we will use latter for fitting. You are also allowed to change the argument after `-d` to a local `.root` file.

For 2+1 channel the workflow is basically the same. You uncomment this line in `gen_outputList.sh`:
```
#classify_files "/store/user/$USER/XHY4bRun3_selection_2p1" "SELECTION_2P1"
```
and run
```
gen_outputList.sh
```
then you generate arguments using `gen_args_pro.sh`:
```
./gen_args_pro.sh division_2p1 selection_2p1
```
and you will see the file `division_2p1_args.txt` created. Copy a line and run it locally with `run_division_2p1.py`.

To run it on GRID, please run
```
eosmkdir /store/user/$USER/XHY4bRun3_division_1p1/
./gridpro.sh division_1p1
```
for 1+1 channel and
```
eosmkdir /store/user/$USER/XHY4bRun3_division_2p1/
./gridpro.sh division_2p1
```
for 2+1 channel.

## Running Limits

### Enviroment
To run Limits, we need to use the *2DAlhpabet* enviroment. Log into lpc9 and go to your working directory and set up the enviroment:
```
cd \your\working\directory\X_HY_4b_Run3
source set_Env_2DA.sh
```
if you want to run jobs on GRID, run
```
./tar_env_2DA.sh
```
check if `tar_2dalphabet.tgz` is created under your eos home directory:
```
eosls /store/user/$USER/
```
### overview
Before running fitting and expected limits, make sure all the division files have been created on eos. Then we go to the directory Limits, which contains everything needed for running limits:
```
cd Limits
```
The general workflow is, we first run `gen_outputList.sh` to generate the output files of the division step, then use `load_fit.sh` to load the templates. Then we use `make_json.sh` to create the json file, `XYH.py` to create the workspace, `run_fit.sh` to fit on the Signal Region, and `load_parameters.C` to load the post-fit parameters. Finally `run_limits.sh` will read the parameters and run `AsymtoticLimits` in `COMBINE`. 
### Local Jobs
We create one directory to store the outputs of the division step and another file to store the templates, and run `gen_outputList.sh` to collect the files:
```
mkdir outputList
mkdir Templates
./gen_outputList.sh
```
Before loading templates, we want to run the limits on a certain signal mass points and channel. For example, if we want to run the "MX-3000_MY-1000" signal on 2+1 channel, then we run:
```
./load_fit.sh 3000 1000 2p1
```
you should see a file `Templates_all_2p1.root` created under `Templates`. Then since we should create the `.json` file for 2p1 channel:
```
./make_json.sh 2p1
```
you will see several `.json` file created targeting different catogories of events. All the other steps are packaged in the `pro.sh` script. you can simply run:
```
./pro.sh 3000 1000
```
and it will create everything you need. 

We can also run the commands in it seperately. Open this file, you will see these two lines
`
python3 XYH.py --tf 1x1 --sig $MX-$MY --r_fail VB1 --r_pass VS2 --make --makeCard --wsp Control_MX-"$MX"_MY-"$MY"`, `
python3 XYH.py --tf 1x1 --sig $MX-$MY --r_fail SB2 --r_pass SR2 --make --makeCard --wsp Loose_MX-"$MX"_MY-"$MY"
`
which create a workspace for the control region \(VB1+VS2\) called `Control_MX-"$MX"_MY-"$MY"_workspace`, and a workspace for the signal region called `Loose_MX-"$MX"_MY-"$MY"_workspace`. 
The next line
`
./run_fit.sh  --fitdir Control_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -b -v 3
`
runs fitting on the Control region, which generate the output file `Control_MX-3000_MY-1000_workspace/SignalMC_XHY4b_1x1_area/higgsCombineSnapshot.MultiDimFit.mH125.root`. Then 
`
root -b -q load_parameters.C\(\"$control_file\"\)
`
loads the post-fit parameters to `control_parameters.txt`. Finally,
`
./run_limits.sh --fitdir Loose_MX-"$MX"_MY-"$MY"_workspace/SignalMC_XHY4b_1x1_area/ -l -v 2
`
generates the limits in the asimov signal region and store the limits in `Loose_MX-3000_MY-1000_workspace/SignalMC_XHY4b_1x1_area/higgsCombine.AsymptoticLimits.mH125.123456.root`.

### GRID Jobs
most of the steps have been automated remotely on GRID. There are still several things you need to do before submitting jobs, though. Firstly, we still need to collect the division files locally:
```
mkdir -p outputList
./gen_outputList.sh
```
then we create the arguments:
```
./gen_args_limits.sh
```
you will see a file called `limits_args.txt` generated. Finally, we need to create the directory on eos file system to store the output:
```
eosmkdir /store/user/$USER/XHY4bRun3_limits_1p1
eosmkdir /store/user/$USER/XHY4bRun3_limits_2p1
```
Finally we are ready to submit the jobs:
```
./gridpro.sh
```

