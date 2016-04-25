from kazoo.recipe.election import Election
from client import ClientBase
import client
from twisted.internet import reactor


class ClientElection(ClientBase):

    def __init__(self, z_node):
        ClientBase.__init__(self,z_node)

    @client.complete_task
    def election_won(self,hostname):
        self.counter['success']+=1
        #time.sleep(random.gammavariate(0.7,0.2))
        #print 'Exiting...'

    @client.timer
    def leader_election(self):
        self.election = Election(self.zk, self.z_node, identifier = self.hostname)
        self.election.run(self.election_won,self.hostname)



def benchmark(func):
    i=0
    func()
    reactor.callInThread(benchmark, func)


if __name__ == '__main__':

    st = ClientElection('/erection')
    reactor.callInThread(benchmark,st.leader_election)
    reactor.run()

