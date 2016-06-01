import sys
#import threading

running = True

def benchmark(cls,func):
    while running:
        func(cls)
    #reactor.callInThread(benchmark, cls, func)

def clientRunner(cls,func):
    my_class = cls(sys.argv[1],sys.argv[2])
    try:
        benchmark(my_class,func)
    except KeyboardInterrupt:
        running = False
    #test = threading.Thread( target=benchmark, args=(my_class,func) )
    #test.start()
    #test.join()
    #reactor.callInThread(benchmark, my_class, func)
    #reactor.run()

