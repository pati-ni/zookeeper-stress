source zk-config.sh
echo $CONFFILE
i=0
ZK=$HOME/zookeeper/server/zookeeper
case $3 in
start)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"rm -rf ${options[dataDir]} ;mkdir -p ${options[dataDir]} ;\
                echo $i >${options[dataDir]}/myid;\
                $ZK $3 $CONFFILE\""
        done
        ;;
stop)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"\
                        $ZK $3 $CONFFILE;\""
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
