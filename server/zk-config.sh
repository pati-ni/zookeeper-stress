#!/bin/bash

ARGS_NUM=2
if [ $# -lt $ARGS_NUM ]
then
    echo "Usage: $0 <nodes-list-filename> <config-file>"
    exit
fi


SOURCEFILE=$2
CONFFILE=/var/tmp/cs091747/zookeeper/zoo.cfg
echo DYNAMICFILE
declare -A options

CLIENTPORT=9666
options["tickTime"]=2000
#options["clientPort"]=9666
options["standaloneEnabled"]=false
options["dataDir"]=/media/localhd/cs091747/zk/data
options["dataLogDir"]=/var/tmp/cs091747/zk
options["initLimit"]=5
options["syncLimit"]=2
options["dynamicConfigFile"]="$CONFFILE.dynamic"
options["maxClientCnxns"]=0
#options["globalOutstandingLimit"]=50000
options["forceSync"]=no

QUORUMPORT1=12888
QUORUMPORT2=13888
DYNAMICFILE="$(dirname ${SOURCEFILE})/$(basename ${options["dynamicConfigFile"]})"
nodes=()
while read -r line;do
    for word in $line; do
	nodes+=("$word")
    done
done < $1

function write_config {
    echo "Creating configuration for zookeeper in $CONFFILE"
    echo "Nodes Active: ${nodes[@]}"
    
    rm $SOURCEFILE &> /dev/null


    for key in ${!options[@]};do
	echo "${key}=${options[${key}]}">>$SOURCEFILE
    done

    local i=0
    ids=()
    rm $DYNAMICFILE &> /dev/null
    for node in ${nodes[@]}
    do
	((i++))
	ids+=($i)
	echo "server.$i=$node:$QUORUMPORT1:$QUORUMPORT2;$CLIENTPORT" >> $DYNAMICFILE
    done
    echo "Config file create on $CONFFILE"
}
