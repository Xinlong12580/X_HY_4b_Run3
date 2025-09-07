export ANA_TOP=$(pwd | sed 's:$:/:' )
source  $(dirname $(readlink -f $BASH_SOURCE))/../Env_Run3_dev/timber-env/bin/activate
