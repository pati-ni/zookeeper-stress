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
#options["maxClientCnxns"]=0
#options["globalOutstandingLimit"]=50000
options["forceSync"]=no

options["zookeeper.nio.numSelectorThreads"]=8
options["zookeeper.nio.numWorkerThreads"]=8
options["zookeeper.commitProcessor.numWorkerThreads"]=32

options["autopurge.snapRetainCount"]=3
options["autopurge.purgeInterval"]=2
#options["syncEnabled"]=false
#options["leaderServes"]=no

QUORUMPORT1=12888
QUORUMPORT2=13888
DYNAMICFILE="$(dirname ${SOURCEFILE})/$(basename ${options["dynamicConfigFile"]})"

OBSERVERS=0

nodes=()
while read -r line;do
    for word in $line; do
	nodes+=("$word")
    done
done < $1

ids=()
for node in ${nodes[@]}
do
	((i++))
	ids+=($i)
done

function write_config {
    echo "Creating configuration for zookeeper in $CONFFILE"
    echo "Nodes Active: ${nodes[@]}"
    
    rm $SOURCEFILE &> /dev/null


    for key in ${!options[@]};do
	echo "${key}=${options[${key}]}">>$SOURCEFILE
    done

    local i=0
    rm $DYNAMICFILE &> /dev/null
    for node in ${nodes[@]}
    do

        if (( "$i" < "$OBSERVERS" ));
        then
            echo "server.${ids[i]}=$node:$QUORUMPORT1:$QUORUMPORT2:observer;$CLIENTPORT" >> $DYNAMICFILE
        else
            echo "server.${ids[i]}=$node:$QUORUMPORT1:$QUORUMPORT2:participant;$CLIENTPORT" >> $DYNAMICFILE
        fi
        ((i++))

    done
    echo "Config file create on $CONFFILE"
}
