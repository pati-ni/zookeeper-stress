#!/bin/bash
source ./env.sh
nodes=("node09" "node15" "node14" "node10" "node11" "node12" "node13")

ARGS_NUM=1
CLIENT_NAME="kz-client.py"

if [[ $# -lt $ARGS_NUM ]]
then
    echo "$# $ARGS_NUM"
    echo "Usage: $0 <command> <optional-args>"
    exit 1
fi

case $1 in
    start)
	for node in $(seq 1 $2);do
	    client=${nodes[$RANDOM % ${#nodes[@]} ]}
	    echo "Starting client in $client"
	    ssh $client "bash $SCRIPT_DIR/start-client.sh $CLIENT_NAME"  &
	done
	;;
    stop)
	echo "Stopping clients in active nodes"
	for node in ${nodes[@]};do
	    ssh $node  "bash $SCRIPT_DIR/stop-client.sh $CLIENT_NAME" 
	done
	killall ssh &> /dev/null
	;;
    *)
       echo "shit"

esac
