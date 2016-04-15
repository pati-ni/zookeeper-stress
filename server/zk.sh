#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $SCRIPT_DIR/zk-config.sh

echo $CONFFILE

ZK=$SCRIPT_DIR/zookeeper


case $3 in
    start)
	write_config
	i=0
        for node in ${nodes[@]}
        do
            echo "$node id ${ids[$i]}"
            ssh $node "bash -c \"\
                rm -rf ${options[dataDir]} ;\
                rm -rf ${options[dataLogDir]};\
                rm -rf /var/tmp/cs091747/zookeeper;\
                mkdir -p ${options[dataDir]} ;\
                mkdir -p /var/tmp/cs091747/zookeeper;\
                mkdir -p ${options[dataLogDir]} ;\
                echo ${ids[i]} >${options[dataDir]}/myid;\
		cp ${SOURCEFILE}* /var/tmp/cs091747/zookeeper
                $ZK start $CONFFILE\""
	    ((i++))
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
	    client=${avail_nodes[ $RANDOM % ${#avail_nodes[@]} ]}
	    avail_nodes=( ${avail_nodes[@]/$client} )
	    selected_nodes+=($client)
	done
	for node in ${selected_nodes[@]};do
	    echo "Killing zookeeper instance on node $node"
	    ssh $node "$SCRIPT_DIR/crash-zk.sh 300"
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
