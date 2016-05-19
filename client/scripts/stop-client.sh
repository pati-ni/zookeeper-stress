#!/bin/bash

echo "$(hostname): Killing $(ps -aux | grep $1  | grep python |grep -v grep | wc -l) $1 client instances"
ps aux | grep $1 | grep -v grep | grep python | awk '{print $2}' | xargs -r kill -9
