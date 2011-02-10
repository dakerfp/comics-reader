
import threading
from Queue import Queue


class JobExecutor(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.__queue = queue
        self.__stop = threading.Event()

    def stop(self):
        self.__stop.set()

    def run(self):
        while not self.__stop.isSet():
            job, args, kwargs = self.__queue.get()
            job(*args, **kwargs)

class BackgroundServer(object):

    def __init__(self, pool_size=1):
        self.__queue = Queue()
        self.__executors = [JobExecutor(self.__queue) for i in range(pool_size)]

    def start(self):
        for executor in self.__executors:
            executor.start()

    def stop(self):
        for executor in self.__executors:
            executor.stop()

    def process(self, job, args, kwargs):
        self.__queue.put((job, args, kwargs))


def background(server):
    """ Decorator to execute jobs in a background server
    """
    def background_job(job):
        def background_call(*args, **kwargs):
            server.process(job, args, kwargs)
        return background_call

    return background_job
