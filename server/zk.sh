#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $SCRIPT_DIR/zk-config.sh

echo $CONFFILE

ZK=$SCRIPT_DIR/zookeeper

LOGGER_NODE=node09
LOGGER_CONF=$HOME/zoo_log.cfg
LOGGER_DATADIR=/media/localhd/cs091747/zk-logger/data
LOGGER_DATALOGDIR=/var/tmp/cs091747/zk-logger


case $3 in
    start)
        #logger
        ssh $LOGGER_NODE "bash -c \"\
                rm -rf $LOGGER_DATADIR ;\
                rm -rf $LOGGER_DATALOGDIR;\
                rm -rf /var/tmp/cs091747/zookeeper-logger;\
                mkdir -p $LOGGER_DATADIR ;\
                mkdir -p /var/tmp/cs091747/zookeeper-logger;\
                mkdir -p $LOGGER_DATALOGDIR ;\
                echo 1 > $LOGGER_DATALOGDIR/myid;\
		        cp  $LOGGER_CONF /var/tmp/cs091747/zookeeper/;\
                $ZK start $LOGGER_CONF\""
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
                echo ${ids[i]} > ${options[dataDir]}/myid;\
		        cp ${SOURCEFILE}* /var/tmp/cs091747/zookeeper/;\
                $ZK start $CONFFILE\""
	        ((i++))
        done


    ;;
    stop)
            ssh $LOGGER_NODE "bash -c \"\
		    $ZK $3 $LOGGER_CONF;
                rm -rf $LOGGER_DATADIR;\
                rm -rf $LOGGER_DATALOGDIR\""

        for node in ${nodes[@]}
        do
            ((i++))
            echo "$node"
            ssh $node "bash -c \"\
		    $ZK $3 $CONFFILE;
                rm -rf ${options[dataDir]} ;\
                rm -rf ${options[dataLogDir]};\
                rm -rf /var/tmp/cs091747/*;
                rm -rf /media/localhd/cs091747/*\""
        done

    ;;
    reconfig)
        write_config
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
