#while IFS= read -r line; do
#    read MX MY <<< $line
#    python load_fit_TH.py --mx $MX --my $MY --mode 2p1 --type signal
#done < ../raw_nano/GoodMassPoints.txt
python load_fit_TH.py --mx $1 --my $2 --mode $3 --type all
#python load_fit_TH.py --mx 1000 --my 300 --mode 2p1 --type bkg
