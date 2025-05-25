input_file=$1
year=$2
output_file=$3
n_files=$4

echo $input_file
ntotal_files=$(wc -l < $input_file)
echo $ntotal_files
i=0
while ((( i * n_files ) <  ntotal_files )); do
    echo -d $input_file -y $year -n $n_files -i $i  >> $output_file
    (( i++ ))
    #echo $i
done
