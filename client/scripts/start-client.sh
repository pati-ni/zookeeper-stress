#!/bin/bash
source "$HOME/zookeeper/client/scripts/env.sh"
source "$PROJECT_DIR/zk-env/bin/activate"
echo "$(hostname): Starting $1 client instance"
python "$CLIENT_DIR/$1" 1> /dev/null

