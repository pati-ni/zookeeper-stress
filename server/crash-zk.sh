#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Killing zookeeper instance on $(hostname)"
ps aux | grep zookeeper | grep java | grep -v grep | awk '{print $2}'| xargs kill -9
sleep_time="$((( ( $RANDOM % $1 ) )+1))"
echo "Sleeping for $sleep_time seconds"
sleep $sleep_time
echo "$(hostname): Starting zookeeper"
$SCRIPT_DIR/zookeeper start ~/zoo.cfg
