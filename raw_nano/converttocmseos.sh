xroot_fs=$( ls files_xrootd)
for xroot_f in $xroot_fs; do
    if [[ $xroot_f == *"Data"* && $xroot_f != *"2023BPix"* ]]; then
        echo converting $xroot_f
        sed 's|cmsxrootd|cmseos|g' files_xrootd/$xroot_f > files/$xroot_f
    else
        echo cping $xroot_f
        sed 's|cmsxrootd.fnal.gov|cms-xrd-global.cern.ch|g' files_xrootd/$xroot_f > files/$xroot_f
        #cp files_xrootd/$xroot_f files/$xroot_f
    fi 
done
