year=$1
./get_filesOfProcess.sh -y $year -p Data
./get_filesOfProcess.sh -y $year -p MC_QCDJets 
./get_filesOfProcess.sh -y $year -p MC_WZJets 
./get_filesOfProcess.sh -y $year -p MC_TTBarJets 
./get_filesOfProcess.sh -y $year -p MC_HiggsJets 
./get_filesOfProcess.sh -y $year -p MC_DibosonJets 
./get_filesOfProcess.sh -y $year -p MC_SingleTopJets 
