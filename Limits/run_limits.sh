#!/bin/bash 

##############################################################################
# Script for running blinded limits
#
# 1) Perform the background-only fit using MultiDimFit
#       - NOTE: we do not use FitDiagnostics, as this runs the S+B fit which we do not want right now
# 2) Obtain expected AsymptoticLimits, using the B-only fit result 
#
# USAGE:
#       ./run_blinded.sh [-bl] [--numtoys XYZ] [--seed XYZ] [--tol X.Y] [--strat X] [--verbosity X]
#
###############################################################################

###############################################################################
# Read options from command line 
###############################################################################
bfit=0
limits=0
seed=42
numtoys=100
tol=0.1         # --cminDefaultMinimizerTolerance
strat=0         # --cminDefaultMinimizerStrategy
verbosity=2

options=$(getopt -o "bl" --long "bfit,limits,seed:,numtoys:,fitdir:,fitdir;,strat:,verbosity:" -- "$@")
eval set -- "$options"

while true; do
    case "$1" in
        --strat)
            shift
            strat=$1
            ;;
        -v|--verbosity)
            shift
            verbosity=$1
            ;;
        -b|--bfit)
            bfit=1
            ;;
        -l|--limits)
            limits=1
            ;;
        --seed)
            shift
            seed=$1
            ;;
        -n|--numtoys)
            shift
            numtoys=$1
            ;;
        --tol)
            shift
            tol=$1
            ;;
        --fitdir)
            echo test
            shift
            fitDir=$1
            ;;      
        --)
            shift
            break;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
    shift
done

echo '--------------------------------------------------------'
echo Using the following options:
echo seed      = $seed
echo strat     = $strat
echo tol       = $tol 
echo numtoys   = $numtoys
echo verbosity = $verbosity
echo '--------------------------------------------------------'

#################################################################################
# Setting some variables
#################################################################################
#fitDir='test_workspace/SignalMC_XHY4b_1x1_area'
cwd=`pwd` # current working directory
card="card.txt"
wsm="workspace_masked.root" # Workspace with channel masks

parameters="--setParameters "
while IFS= read -r line; do
    if [[ $line == *"QCD_Rc"* ]]; then
        echo 1
        read var_name var_value <<< "$line"
        parameters=$parameters"$var_name=$var_value,"

    fi
done < control_parameters.txt


parameters=${parameters%?}
echo $parameters
card=card.txt
wsm=card.root
strat=1
#fitDir='w3000_300_workspace/SignalMC_XHY4b_1x1_area'
tot=0.1
seed=123456
if [ $limits = 1 ]; then 
    printf "cd $fitDir \n"
    cd $fitDir

    # Check to see if the workspace with channel masks exists
    if [ ! -f "$wsm" ]; then 
        printf "RooWorkspace with channel masks does not exist, creating it now...\n"
        (set -x; text2workspace.py $card --channel-masks -o $wsm)
        #(set -x; text2workspace.py $card -o $wsm)
    fi

    # Loads the B-only fit snapshot obtained from the prior step, then specifies that we want to run blind
    #(set -x; combine -M AsymptoticLimits -m 125 -n "" -d higgsCombineSnapshot.MultiDimFit.mH125.root --snapshotName MultiDimFit -v $verbosity --saveWorkspace --saveToys --bypassFrequentistFit -s $seed --toysFrequentist --run blind  -t $numtoys)
    (set -x; combine -M AsymptoticLimits -d $wsm -m 125 -n "" -v $verbosity $parameters --saveWorkspace --saveToys --bypassFrequentistFit -s $seed --toysFrequentist --run blind )

    printf "cd $cwd \n"
    cd $cwd
fi
