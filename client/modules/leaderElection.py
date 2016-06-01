from kazoo.recipe.election import Election
from client import ZkBase
import client
from runner import clientRunner

class ClientElection(ZkBase):

    def __init__(self, z_node, id):
        ZkBase.__init__(self, z_node, id)
        self.election = Election(self.zk, self.z_node, identifier=self.hostname)

    @client.complete_task
    def election_won(self,hostname):
        pass
        #time.sleep(random.gammavariate(0.7,0.2))
        #print 'Exiting...'
    @client.timer
    def leader_election(self):
        self.election.run(self.election_won,self.hostname)


if __name__ == '__main__':
    clientRunner(ClientElection,ClientElection.leader_election)
