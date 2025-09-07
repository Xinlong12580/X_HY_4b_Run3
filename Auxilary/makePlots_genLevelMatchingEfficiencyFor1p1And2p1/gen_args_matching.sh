> matching_args.txt
while IFS= read -r line; do
    arr=($line)
    echo --mx ${arr[0]} --my ${arr[1]}
    echo --mx ${arr[0]} --my ${arr[1]} >> matching_args.txt
done < raw_nano/GoodMassPoints.txt
