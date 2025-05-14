# Xinlong Run 3 X->HY->4b analysis

Files located under `/uscms/home/xinlongl/nobackup/projects/XHY4bRun3/X_HY_4b_Run3/hists_division_TH.pkl`

## 2DAlphabet installation

Follow the instructions here: https://github.com/JHU-Tools/2DAlphabet/tree/el9_matplotlib_plotting?tab=readme-ov-file#installation-instructions

Instructions copied below:
```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.0.1
cd ../../
git clone --branch CMSWW_14_1_0_pre4 git@github.com:JHU-Tools/CombineHarvester.git
cd CombineHarvester/
cd ..
scramv1 b clean
scramv1 b -j 16
git clone --branch el9_matplotlib_plotting git@github.com:JHU-Tools/2DAlphabet.git
python3 -m virtualenv twoD-env
source twoD-env/bin/activate
cd 2DAlphabet/
python setup.py develop
```

## Running the examples

1. Run `scripts/make_TH2s.py` to open the pickle file and make ROOT files with template TH2s for all processes, regions, and years. The output will be stored under `rootfiles/`.

2. Run `python XYH.py --tf [TF] [--make] [--makeCard] [--fit] [--plot]`
    * `--tf [TF]` is the transfer function parameterization you want to try. Options are: `0x0`, `0x1`, `1x0`, `1x1`, `2x1`, `1x2`, `2x2`, etc
    * `--make`: this flag tells the script to create the 2DAlphabet workspace. Only needs to be run once 
    * `--makeCard`: This flag tells the script to generate a Combine card (which describes the likelihood model) for the requested TF
    * `--fit`: Run the maximum likelihood fit for the background-only and signal-plus-background hypothesis for the requested TF
    * `--plot`: Plot the post-B-only and post-S+B fit results for the requested TF. 

Example: 

First generate the workspace:
```
python XYH.py --tf blah --make 
```
(specify a random value for the TF, it's a required argument but doesn't matter for making the workspace)

Then let's say we want to try fitting the constant (`0x0`) TF model:

```
python XYH.py --tf 0x0 --makeCard --fit
```

Check the output of the fit from Combine to make sure it's ok.

Then to plot it, 
```
python XYH.py --tf 0x0 --plot
```

