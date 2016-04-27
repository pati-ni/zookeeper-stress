from twisted.internet import reactor
import sys

def benchmark(cls,func):
    func(cls)
    reactor.callInThread(benchmark, cls, func)

def clientRunner(cls,func):
    my_class = cls(sys.argv[1],sys.argv[2])
    reactor.callInThread(benchmark, my_class, func)
    reactor.run()

