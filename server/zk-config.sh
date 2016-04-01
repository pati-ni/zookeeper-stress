#!/bin/bash

ARGS_NUM=2
if [ $# -lt $ARGS_NUM ]
then
	echo "Usage: $0 <nodes-list-filename> <config-file>"
	exit
fi

CONFFILE=$2

declare -A options

options["tickTime"]=2000
options["clientPort"]=9666
options["dataDir"]=/var/tmp/cs091747/zk/data
options["initLimit"]=5
options["syncLimit"]=2
#options["globalOutstandingLimit"]=50000
options["forceSync"]=no

QUORUMPORT1=12888
QUORUMPORT2=13888

nodes=()
while read -r line;do
	for word in $line; do
		nodes+=("$word")
	done
done < $1
echo "Creating configuration for zookeeper in $2"
echo "Nodes Active: ${nodes[@]}"

rm $CONFFILE &> /dev/null


for key in ${!options[@]};do
    echo "${key}=${options[${key}]}">>$CONFFILE
done


i=0
for node in ${nodes[@]}
do
	((i++))
	echo "server.$i=$node:$QUORUMPORT1:$QUORUMPORT2" >> $CONFFILE
done



