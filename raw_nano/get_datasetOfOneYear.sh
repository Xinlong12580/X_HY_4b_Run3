year=$1
./get_dataset.sh -y $year -d Data
./get_dataset.sh -y $year -d MC_QCDJets 
./get_dataset.sh -y $year -d MC_WZJets 
./get_dataset.sh -y $year -d MC_TTBarJets 
./get_dataset.sh -y $year -d MC_HiggsJets 
./get_dataset.sh -y $year -d MC_DibosonJets 
./get_dataset.sh -y $year -d MC_SingleTopJets 
