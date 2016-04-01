#!/bin/bash

if [ $# -lt 1 ];then
    echo "Usage: $0 <command> <optional-args>"
    exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NODESLIST="$SCRIPT_DIR/server/nodes_list"

case $1 in
    start)
	if [ $# -lt 2 ];then
	    echo "Please supply the number of clients you wish to start"
	    exit 1
	fi
	./server/zk.sh $NODESLIST ~/zoo.cfg $1
	./client/scripts/clients.sh $1
	;;
    start-clients)
	if [ $# -lt 2 ];then
	    echo "Please supply the number of clients you wish to start"
	    exit 1
	fi
	./client/scripts/clients.sh start $2 
	;;
    start-server)
	./server/zk.sh $NODESLIST ~/zoo.cfg start
	;;
    stop)
	./server/zk.sh $NODESLIST ~/zoo.cfg $1
	./client/scripts/clients.sh $1
	;;
    *)
	echo "Unknown command $1" 


esac
