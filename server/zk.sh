source zk-config.sh

i=0
case $3 in
start)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"mkdir -p ${options[dataDir]};\
                echo $i >${options[dataDir]}/myid;\
                zookeeper $3 $CONFFILE\""
        done
        ;;
stop)
        for node in ${nodes[@]}
        do
                ((i++))
                echo "$node"
                ssh $node "bash -c \"\
                        zookeeper $3 $CONFFILE;
                        fuser -k 2181/tcp\""
        done
        ;;
*)
        for node in ${nodes[@]}
        do
                ((i++))
                ssh $node "bash -c \"zookeeper $3 $CONFFILE\""
        done
        ;;
esac
