#while IFS= read -r line; do
#    read MX MY <<< $line
#    python load_fit_TH.py --mx $MX --my $MY --mode 2p1 --type signal
#done < ../raw_nano/GoodMassPoints.txt
rm Templates/*
python load_fit_TH.py --mx $1 --my $2 --mode All1p1 --type all
python load_fit_TH.py --mx $1 --my $2 --mode All2p1 --type all
python load_fit_TH.py --mx $1 --my $2 --mode Only1p1 --type all
python load_fit_TH.py --mx $1 --my $2 --mode Only2p1 --type all
hadd Templates/Templates_All1p1_Only2p1_all.root Templates/Templates_All1p1_all.root Templates/Templates_Only2p1_all.root 
hadd Templates/Templates_All2p1_Only1p1_all.root Templates/Templates_All2p1_all.root Templates/Templates_Only1p1_all.root 
#python load_fit_TH.py --mx 1000 --my 300 --mode 2p1 --type bkg
