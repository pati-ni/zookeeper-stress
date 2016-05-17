#!/bin/bash

#Script that manages the experiments

if [ $# -lt 1 ];then
    echo "Usage: $0 <command> <optional-args>"
    exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NODESLIST="$SCRIPT_DIR/server/nodes_list"

function stop_clients {
    for client in $(ls $SCRIPT_DIR/client/modules/*.py);
    do
        echo "killing client $client"
        ./client/scripts/clients.sh stop $(basename $client)
    done

}


case $1 in
    start)
	    ./server/zk.sh $NODESLIST ~/zoo.cfg start
	    #./client/scripts/clients.sh start $2
	;;
    stop-clients)
        stop_clients
	;;
    start-server)
	    ./server/zk.sh $NODESLIST ~/zoo.cfg start
	;;
    kill-zookeeper)
        if [ $# -lt 2 ];then
            echo "Please supply the number of zookeeper instances you wish to kill"
            exit 1
        fi
        ./server/zk.sh $NODESLIST ~/zoo.cfg kill $2
	;;
    stop)
        stop_clients
        ./server/zk.sh $NODESLIST ~/zoo.cfg $1
	;;
    *)
	echo "Unknown command $1" 

esac
