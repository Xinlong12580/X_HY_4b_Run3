input_file=$1
year=$2
region=$3
output_file=$4

echo $input_file
echo -d $input_file -y $year -n 1 -i 0 -r $region >> $output_file
