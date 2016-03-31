#!/bin/bash
source ./env.sh
source $PROJECT_DIR/zk-env/bin/activate
echo "$(hostname): Starting $1 client instance"
python $CLIENT_DIR/$1

