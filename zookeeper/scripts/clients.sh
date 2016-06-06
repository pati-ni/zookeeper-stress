#!/bin/bash
source "$HOME/zookeeper/client/scripts/env.sh"

nodes=()
while read -r line;do
    for word in $line; do
	nodes+=("$word")
    done
done < client/node_list

ARGS_NUM=1
#CLIENT_NAME="kz-leaderElection.py"

if [[ $# -lt $ARGS_NUM ]]
then
    echo "$# $ARGS_NUM"
    echo "Usage: $0 <command> <optional-args>"
    exit 1
fi

function client_start {
    if [[ $1 -eq "0" ]]
    then
	return
    fi
    local i=0
    for node in $(seq 1 $1);do
        ((i++))
        #echo "Starting client in $client"
        #echo "$SCRIPTS_DIR/start-client.sh $CLIENT_NAME"
        ssh $2 "bash -c \"screen -dmS $3-$i $SCRIPTS_DIR/start-client.sh $3 \" "
    done
    echo "$2: Batch of $1, client: $3"
}


case $1 in
    start)
	clients=$(( $2 / ${#nodes[@]}  ))
	for node in  ${nodes[@]};do
	    ( client_start $clients $node $3 ) &
	done
	for i in $(seq 1 $(( $2 % ${#nodes[@]} )))
	do
	    node=${nodes[$i % ${#nodes[@]} ]}
	    ( client_start 1 $node $3 ) &
	done
	;;
    stop)
	echo "Stopping clients in active nodes"
	for node in ${nodes[@]};do
	    ssh $node  "$SCRIPTS_DIR/stop-client.sh $2"
	done
	killall ssh &> /dev/null
	;;
    *)
	echo "Unknown command $1"

esac
