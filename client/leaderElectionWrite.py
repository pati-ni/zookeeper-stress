from twisted.internet import reactor
from kazoo.recipe.election import Election
from client import ClientBase
import client

class ClientElection(ClientBase):

    def __init__(self, z_node):
            ClientBase.__init__(self,z_node)

    @client.timer
    def leader_election(self):
        #time.sleep(random.gammavariate(0.7,0.2))
        self.election = Election(self.zk,self.z_node,identifier=self.hostname)
        self.election.run(self.election_won,self.hostname)

    @client.complete_task
    def election_won(self,hostname):
        #print 'Success',hostname,'Synthetic workload running...'
        self.counter['success']+=1
        self.zk.set(self.z_node,str(self.counter['success']))
        #print 'Exiting...'

def benchmark(func):
    i=0
    func()
    reactor.callInThread(benchmark, func)


if __name__ == '__main__':
    st = ClientElection('/erection')
    reactor.callInThread(benchmark,st.leader_election)
    reactor.run()
    
