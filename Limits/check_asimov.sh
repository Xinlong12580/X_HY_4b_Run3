while IFS= read -r line ; do
    if [[ $line != *"AsymptoticLimits"* ]]; then
        continue
    fi
    echo $line
    rm root/*
    xrdcp $line root/tmp.root
    read MX < <(echo $line | awk -F'_' '{print $4}')
    read MY < <(echo $line | awk -F'_' '{print $5}')
    echo  $MX $MY
    root -b -q check_asimov.C\(\"$MX\",\"$MY\"\)
    exit
done < outputList/output_limits_2p1.txt 
