#!/bin/bash
source "$HOME/zookeeper/client/scripts/env.sh"
nodes=("node09" "node15" "node14" "node10" "node11" "node12" "node13")

ARGS_NUM=1
CLIENT_NAME="kz-leaderElection.py"

if [[ $# -lt $ARGS_NUM ]]
then
    echo "$# $ARGS_NUM"
    echo "Usage: $0 <command> <optional-args>"
    exit 1
fi

case $1 in
    start)
	for node in $(seq 1 $2);do
	    client=${nodes[$node % ${#nodes[@]} ]}
	    #echo "Starting client in $client"
	    ssh $client "$SCRIPTS_DIR/start-client.sh $CLIENT_NAME"  &
	done
	;;
    stop)
	echo "Stopping clients in active nodes"
	for node in ${nodes[@]};do
	    ssh $node  "$SCRIPTS_DIR/stop-client.sh $CLIENT_NAME" 
	done
	killall ssh &> /dev/null
	;;
    *)
       echo "Unknown command $1"

esac
