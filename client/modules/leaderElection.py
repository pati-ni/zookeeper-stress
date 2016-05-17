from kazoo.recipe.election import Election
from client.client import ClientBase
import client.client
from client.runner import clientRunner

class ClientElection(ClientBase):

    def __init__(self, z_node, id):
        ClientBase.__init__(self, z_node, id)

    @client.client.complete_task
    def election_won(self,hostname):
        self.counter['success']+=1
        #time.sleep(random.gammavariate(0.7,0.2))
        #print 'Exiting...'

    @client.client.timer
    def leader_election(self):
        self.election = Election(self.zk, self.z_node, identifier = self.hostname)
        self.election.run(self.election_won,self.hostname)


if __name__ == '__main__':
    clientRunner(ClientElection,ClientElection.leader_election)
