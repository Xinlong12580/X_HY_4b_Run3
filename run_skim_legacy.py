from skim import *
from argparse import ArgumentParser

parser=ArgumentParser()
parser.add_argument('-f', type=str, dest='input_file',action='store', required=True)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=True)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=True)
args=parser.parse_args()

files = []
file_name = args.input_file

with open(file_name,"r") as f:
    all_files = f.readlines()
    all_files = [line.strip() for line in all_files]
    N=len(all_files)
    i=args.i_job
    if (i * args.n_files) > (N - 1):
        exit()
    if ((i + 1) * args.n_files) <= (N - 1):
        files = all_files[i * args.n_files : (i+1) * args.n_files]
    else:
        files = all_files[i * args.n_files : len(all_files)]
print(N)
print(files)
output = file_name[9:] + f"_{args.n_files}_{args.i_job}.root"
print(output)
skim(files, 1, output)
