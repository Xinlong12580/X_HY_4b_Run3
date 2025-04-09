input_file=$1
year=$2
output_file=$3

echo $input_file
echo -d $input_file -y $year -n 1 -i 0 >> $output_file
