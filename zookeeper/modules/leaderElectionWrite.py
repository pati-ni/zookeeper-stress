from kazoo.recipe.election import Election
from zookeeper.client import ZkBase
import zookeeper.client as client
from zookeeper.runner import clientRunner

class ClientElection(ZkBase):

    def __init__(self, z_node, id):
            #self.wait = 0.6
            ZkBase.__init__(self,z_node, id)

    @client.timer
    def leader_election(self):
        #time.sleep(random.gammavariate(0.7,0.2))
        self.election = Election(self.zk,self.z_node,identifier=self.hostname)
        self.election.run(self.election_won,self.hostname)

    @client.complete_task
    def election_won(self,hostname):
        #print 'Success',hostname,'Synthetic workload running...'
        #self.counter['success']+=1
        self.zk.set(self.z_node,str(self.counter['success']))
        #print 'Exiting...'


if __name__ == '__main__':
    clientRunner(ClientElection,ClientElection.leader_election)
