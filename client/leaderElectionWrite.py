from kazoo.client import KazooClient
from kazoo.recipe.election import Election
from client import ClientBase

class ClientElection(ClientBase):

    def __init__(self, z_node):
            ClientBase.__init__(self,z_node)

    @ClientBase.stopwatch
    def leader_election(self):
        #time.sleep(random.gammavariate(0.7,0.2))
        self.election = Election(self.zk,self.znode,identifier=self.hostname)
        self.election.run(self.election_won,self.hostname)

    @ClientBase.complete_task
    def election_won(self,hostname):
        #print 'Success',hostname,'Synthetic workload running...'
        self.counter+=1
        self.zk.set(self.znode,str(self.counter))
        #print 'Exiting...'


if __name__ == '__main__':

    client = ClientElection('/erection')

    while True:
        client.leader_election()

    
