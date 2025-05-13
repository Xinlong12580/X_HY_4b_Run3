'''
Script to set up the Combine workspace for the Run 3 XYH->4b test
'''
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import os
import numpy as np
import subprocess
import inspect

def _generate_constraints(nparams):
    out = {}
    for i in range(nparams):
        out[i] = {"MIN":-500,"MAX":500}
    return out
Ra = -5.02805e-07
Rb = 0.000211418
Rc = -0.00617309
Rpf = f"{Ra}*x**2+{Rb}*x+{Rc}"

def R_pf_fit(x):
    return (Ra*x**2 + Rb*x + Rc)
_rc_options = {
    '0x0': {
        'form': f'(@0)',
        'constraints': _generate_constraints(1)
    },
    '1x0': {
        'form': f'((@0+@1*x))',
        'constraints': _generate_constraints(2)
    },
    '0x1': {
        'form': f'((@0+@1*y))',
        'constraints': _generate_constraints(2)
    },
     '1x1': {
        'form': f'((@0+@1*x)*(@2+@3*y))',
        'constraints': _generate_constraints(4)
    },
    '2x1': {
        'form': f'(@0+@1*x+@2*x**2)*(@3+@4*y)',
        'constraints': _generate_constraints(5)
    },
    '2x2': {
        'form': f'(@0+@1*x+@2*x**2)*(@3+@4*y*@5*y**2)',
        'constraints': _generate_constraints(6)
    },
    '3x1': {
        'form': f'(@0+@1*x+@2*x**2+@3*x**3)*(@4+@5*y)',
        'constraints': _generate_constraints(6)
    }
}
print(f'({Rpf})*(@0*x*y+@1*x+@3*y+@2)')
_rc_options = {
    '1x1': {
        'form': f'(@0*x*y+@1*x+@3*y+@2)',
        'constraints': _generate_constraints(4)
    }
}

def _select_signal(row, args):
    # Two arguments are passed to this function: the signal name (as it appears in the ledger), and the TF parameterization.
    signame = args[0]
    tf      = args[1]

    # This function loops over the ledger and selects rows which contain (1) the signal we are requesting, and (2), the data driven bkg (QCD) in the fail region (VB1) and pass region (VS2) obtained from our requested TF parameterization
    if row.process_type == 'SIGNAL':    # This entry in the ledger (row) is of type "SIGNAL"
        if signame in row.process:  # This is the signal we requested (see args)
            print(f'Adding signal {row.process}')
            return True
        else:   # Otherwise, it's not the signal we requested. This can occur if multiple signals are specified in the `SIGNAME` list in the JSON.
            return False
    elif 'QCD' in row.process:  # Check the `AddAlphaObj()` calls later in this script. Notice that their first argument is the name of the object, which begins with "QCD_". We are going to select (1) the QCD in the fail region, called "QCD_fail", and then the QCD in the pass region obtained from the transfer function parameterization we requested, called "QCD_pass_<tf>"
        if row.process == 'QCD_fail':
            print('Adding QCD fail object in VB1 (fail)')
            return True
        elif tf in row.process:
            print(f'Adding QCD pass object in VS2 (pass) for R_c parameterization {tf}')
            return True
        else:
            return False
    else:
        return True


def make_2DAlphabet_workspace(name='XYH', fr={}, json='XYH.json'):
    # Set up the workspace
    twoD = TwoDAlphabet(
        f'{name}_workspace',    # Name of the workspace directory
        json,                   # Name of the JSON file 
        loadPrevious=False,     # We are not loading a previous workspace, but rather creating an entirely new one
        findreplace=fr          # A dictionary used to find and replace terms in the JSON. Not used for now, but I can show an example later
    )

    # Obtain data-driven QCD estimate as (data - MC bkgs)
    qcd_hists = twoD.InitQCDHists()

    # Get the binning as described in the JSON. It will be the same for both regions, so just choose one
    binning, _ = twoD.GetBinningFor('VB1')
    
    # Set up QCD estimate in VB1 (fail)
    qcd_fail = BinnedDistribution(
        'QCD_fail',         # Name of the distribution
        qcd_hists['VB1'],   # The (data-bkg) QCD estimate for this region
        binning,            # The binning for this region
        constant = False    # Allow QCD estimate to float
    )
    print(type(qcd_fail))
    for name, member in inspect.getmembers(qcd_fail):
        print(name, member)
    # Add it to the 2DAlphabet ledger
    twoD.AddAlphaObj(
        'QCD_fail',     # Object name
        'VB1',          # Region to which it belongs (fail)
        qcd_fail,       # BinnedDistribution object
        title = 'QCD'   # Title for plotting
    )
    R_pf_hist = qcd_hists['VB1'].Clone("R_pf_hist")
    for i in range(1, R_pf_hist.GetNbinsX()+1):       # x-axis
        for j in range(1, R_pf_hist.GetNbinsY()+1):   # y-axis
            bin_center = 1/2*(R_pf_hist.GetXaxis().GetBinLowEdge(i) + R_pf_hist.GetXaxis().GetBinUpEdge(i))
            R_pf_hist.SetBinContent(i,j, R_pf_fit(bin_center))
            print(bin_center,R_pf_fit(bin_center))
    #exit()
    R_pf = BinnedDistribution(
        'R_pf',         # Name of the distribution
        R_pf_hist,   # The (data-bkg) QCD estimate for this region
        binning,            # The binning for this region
        constant = True    # Allow QCD estimate to float
    )

    # Now generate QCD estimates in VS2 (pass) using all RPF options
    for rc_name, rc_opts in _rc_options.items():
        # Create a parameteric function for R_c(MJJ,MJY)
        qcd_Rc = ParametricFunction(
            f'QCD_Rc_{rc_name}',                    # Name of Rc function
            binning,                                # Binning to use
            rc_opts['form'],                        # Rc parameterization
            constraints = rc_opts['constraints']    # Rc parameter constraints
        )
        # Now get the QCD estimate in VS2 (pass)
        qcd_pass_tmp = qcd_fail.Multiply(
            'QCD_pass_tmp',     # Name of the binned distributon representing QCD in VS2
            qcd_Rc          # ParametricFunction object multiplying QCD_fail
        )
        qcd_pass = qcd_pass_tmp.Multiply(
            'QCD_pass',     # Name of the binned distributon representing QCD in VS2
            R_pf          # ParametricFunction object multiplying QCD_fail
        )
        # Add it to the 2DAlphabet ledger
        twoD.AddAlphaObj(
            f'QCD_pass_{rc_name}',  # Object name
            'VS2',                  # Region to which it belongs (pass)
            qcd_pass,               # BinnedDistribution object
            title = 'QCD'           # Title for binning
        )

    # Save it all out
    twoD.Save()

def make_card(name='XYH', signal='', tf=''):
    '''
    Make a Combine card for the given signal and transfer function parameterization
    '''
    working_area = f'{name}_workspace'
    twoD = TwoDAlphabet(
        working_area,                       # The 2DAlphabet workspace name
        f'{working_area}/runConfig.json',   # A copy of the JSON that gets made when creating a 2DAlphabet workspace
        loadPrevious = True                 # In this case, we want to load the already created workspace.
    )
    # Get a subset of the ledger containing our signal of interest and the QCD estimate created by our TF parameterization
    subset = twoD.ledger.select(_select_signal, signal, tf)
    twoD.MakeCard(
        subset, 
        f'{signal}_{tf}_area'   # Name of the subdirectory in the main 2DAlphabet workspace for this TF parameterization
    )

def FitDiagnostics(name='XYH', signal='', tf='', defMinStrat=0, extra='--robustHesse 1', rMin=-1, rMax=10, setParams={}, verbosity=2):
    working_area = f'{name}_workspace'
    twoD = TwoDAlphabet(working_area, f'{working_area}/runConfig.json',loadPrevious = True)
    subset = twoD.ledger.select(_select_signal, signal, tf)
    twoD.MLfit(
        f'{signal}_{tf}_area',      # Subdirectory for this TF parameterization
        rMin=rMin,                  # Signal strength ("r") minimum allowed value
        rMax=rMax,                  # Signal strength ("r") maximum allowed value
        setParams=setParams,        # {param:value} dict specifying parameters in the likelihood to set manually
        verbosity=verbosity,        # Combine output verbosity (2 is the sweet spot)
        defMinStrat=defMinStrat,    # Default minimizer strategy
        extra=extra                 # Any extra args to pass to the fit routine
    )

def plot_postfit(name='XYH', signal='', tf=''):
    working_area = f'{name}_workspace'
    twoD = TwoDAlphabet(working_area, f'{working_area}/runConfig.json',loadPrevious = True)
    subset = twoD.ledger.select(_select_signal, signal, tf)
    # Customize the plots to include region definitions in the plots.
    # The key must be the REGION specified in the JSON, the value is the text to appear in the plot
    subtitles = {
        'VB1': 'VB1 (fail)',
        'VS2': 'VS2 (pass)'
    }
    twoD.StdPlots(
        f'{signal}_{tf}_area',
        subset,
        subtitles=subtitles
    )


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-w', type=str, dest='workspace',
                        action='store', default='XYH',
                        help='workspace name')
    parser.add_argument('--tf', type=str, dest='tf',
                        action='store', required=True,
                        help='TF parameterization choice for the fit')
    parser.add_argument('--make', dest='make',
                        action='store_true', 
                        help='If passed as argument, create 2DAlphabet workspace')
    parser.add_argument('--makeCard', dest='makeCard',
                        action='store_true', 
                        help='If passed as argument, create Combine card for given TF parameterization')
    parser.add_argument('--fit', dest='fit',
                        action='store_true',
                        help='If passed as argument, fit with the given TF')
    parser.add_argument('--plot', dest='plot',
                        action='store_true',
                        help='If passed as argument, plot the result of the fit with the given TF')

    args = parser.parse_args()

    if args.make:
        make_2DAlphabet_workspace()

    if args.makeCard:
        make_card(signal='MX-3000_MY-300_2022', tf=args.tf)

    if args.fit:
        FitDiagnostics(signal='MX-3000_MY-300_2022', tf=args.tf)

    if args.plot:
        plot_postfit(signal='MX-3000_MY-300_2022', tf=args.tf)
