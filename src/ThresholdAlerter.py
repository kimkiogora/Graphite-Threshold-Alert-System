#######################################################
# @Author	: Kim Kiogora	<kimkkiogora@gmail.com>
# @version	: 2.0 , 15/01/12
# @Usage    : Alerts for graphite
#######################################################
import time
from threading import Thread
from QueuePool import QueueManager
from ParentTask import Task
from Utilities import CUtility
import sys
import socket
import  os

global queue
CUtils = CUtility()

# The class itself
class Parent:
    mypool = None

    # An empty constructor
    def __init__(self):
        CUtils.logger('Locating config file = '+CUtils.CONFIG_FILE+'...')
        if os.path.exists(CUtils.CONFIG_FILE):
            CUtils.logger('Found config file = '+CUtils.CONFIG_FILE+'...')
            CUtils.load_properties()
        else:
            CUtils.infoLog.error('Config file = '+CUtils.CONFIG_FILE+' not found, exitting...')
            self.die('Property file does not exist!')

        CUtils.logger("Initializing the queue with workers")
        """ Initialize the pool with  workers """
        self.mypool = QueueManager(CUtils.MAX_CHILD_PROCESSES)

    # Wait a few seconds before proceeding with a task
    def do_wait(self, sec):
        time.sleep(sec)

    # exit gracefully
    def die(self, reason):
        """Exits and Log your reason"""
        sys.exit()

    # Creates a simple Runnable that holds a Job object thats worked on by the
    # children threads.
    def create_task(self, data):
        """Pass your data to the worker"""
        task = Task(data);
        task.processData()

    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('localhost', 10000)
        CUtils.logger('starting up on %s port %s' % server_address)
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(1)
        while True:
            # Wait for a connection
            CUtils.logger('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                CUtils.logger('connection from', client_address)
                data = connection.recv(1024)
                CUtils.logger('received "%s"' % data)
                response = 'OK'
                CUtils.logger('Send response %s' % response)
                connection.sendall(response)
                CUtils.logger('Sent')
                
                "set to non-blocking IO, then process request"
                #create_task(data)
            finally:
                # Clean up the connection
                connection.close()

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
