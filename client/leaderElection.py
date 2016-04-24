from kazoo.recipe.election import Election
from client import ClientBase


class ClientElection(ClientBase):
    def __init__(self, znode):
        ClientBase.__init__(znode)


    @ClientBase.stopwatch
    def leader_election(self):
        self.election = Election(self.zk,self.znode,identifier=self.hostname)
        self.election.run(self.election_won,self.hostname)

    @ClientBase.complete_task
    def election_won(self,hostname):
        #print 'Success',hostname,'Synthetic workload running...'
        self.counter+=1
        #time.sleep(random.gammavariate(0.7,0.2))
        #print 'Exiting...'



if __name__ == '__main__':
    client = ClientElection('/erection')
    while True:
        client.leader_election()
