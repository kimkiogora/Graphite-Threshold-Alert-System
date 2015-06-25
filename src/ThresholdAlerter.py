#######################################################
# @Author	: Kim Kiogora	<kimkkiogora@gmail.com>
# @version	: 2.0 , 25/06/16
# @Usage    : Threshhold AlertMan for graphite data
#######################################################
import time
from threading import Thread
from QueuePool import QueueManager
from ParentTask import Task
import sys

global queue

# The class itself
class Parent:
    global mypool

    # An empty constructor
    def __init__(self):
        """ Initialize the pool with 2 workers """
        self.mypool = QueueManager(2)

        # Wait a few seconds before proceeding with a task

    def doWait(self, sec):
        time.sleep(sec)

        # exit gracefully

    def die(self, reason):
        """Exits and Log your reason"""
        sys.exit()

        # Creates a simple Runnable that holds a Job object thats worked on by the
        # children threads.

    def createTask(self, data):
        """Pass your data to the worker"""
        task = Task(data);
        task.processData()

        # Main Entry point for the service

    def run(self):
        while True:
            """ Fetch your data from some source """
            some_data = 'My data, maybe from a database or URL'

            self.mypool.add_task(self.createTask, some_data)
            self.mypool.wait_completion()

            """Sleep for a bit"""
            print 'Loop'

            self.doWait(float(1))

    # function to start the service process
    def start(self):
        try:
            master = Thread(target=self.run)
            master.start()
        except Exception, er:
            self.die('Unable to create main thread, will exit')


# Initialize the service
def run_service():
    pusher = Parent()
    pusher.start()

# Important: the modules should not execute code
# when they are imported
if __name__ == '__main__':
    run_service()
    ###############################
    # END CLASS
    ###############################
