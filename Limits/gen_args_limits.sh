> limits_args.txt
while IFS= read -r line; do
    echo $line SB2 SR2 1p1
    #echo $line SB2 SR2 1p1 >> limits_args.txt
    echo $line SB2 SR2 2p1 >> limits_args.txt
done < ../raw_nano/GoodMassPoints.txt
