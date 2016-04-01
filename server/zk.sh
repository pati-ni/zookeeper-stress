#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $SCRIPT_DIR/zk-config.sh

echo $CONFFILE
i=0
ZK=$SCRIPT_DIR/zookeeper


case $3 in
start)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"rm -rf ${options[dataDir]} ;mkdir -p ${options[dataDir]} ;\
                echo $i >${options[dataDir]}/myid;\
                $ZK $3 $CONFFILE\""
        done
        ;;
stop)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"\
                        $ZK $3 $CONFFILE;\""
        done
        ;;
kill)
    avail_nodes=("${nodes[@]}")
    selected_nodes=()
    for i in $(seq 1 $4);do
	echo "Got here"
	client=${avail_nodes[ $RANDOM % ${#avail_nodes[@]} ]}
	avail_nodes=( ${avail_nodes[@]/$client} )
	selected_nodes+=($client)
    done
    for node in ${selected_nodes[@]};do
	echo "Killing zookeeper instance on node $node"
	ssh $node "$SCRIPT_DIR/crash-zk.sh 20"
    done
       ;;
*)
        for node in ${nodes[@]}
        do
                ((i++))
                ssh $node "bash -c \"$ZK $3 $CONFFILE\""
        done
        ;;
esac
