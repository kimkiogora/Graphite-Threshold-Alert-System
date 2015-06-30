# @Author   : Kim Kiogora	<kimkkiogora@gmail.com>
# @Usage    : Alerts for graphite
# Version   : 1.0
# Since     : 28 June 2015
import time
from threading import Thread
from QueuePool import QueueManager
from ParentTask import Task
from Utilities import CUtility
import sys
import socket
import os

CUtils = CUtility()

# The class itself
class Parent:

    # An empty constructor
    def __init__(self):
        CUtils.logger('Locating config file = ' + CUtils.CONFIG_FILE + '...')
        if os.path.exists(CUtils.CONFIG_FILE):
            CUtils.logger('Found config file = ' + CUtils.CONFIG_FILE + '...')
            CUtils.load_properties()
        else:
            CUtils.infoLog.error('Config file = ' + CUtils.CONFIG_FILE + ' not found, exiting...')
            self.die('Property file does not exist!')

    # Wait a few seconds before proceeding with a task
    def do_wait(self, sec):
        time.sleep(sec)

    # exit gracefully
    def die(self, reason):
        """Exits and Log your reason"""
        sys.exit()

    # Worker
    def create_task(self, data):
        """Pass your data to the worker"""
        task = Task(data, CUtils)
        task.process_data()

    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('localhost', CUtils.GAT_PORT)
        CUtils.logger('starting up on %s port %s' % server_address)
        sock.bind(server_address)
        sock.listen(CUtils.MAX_CHILD_PROCESSES)
        CUtils.logger("Initializing the queue with workers")
        """ Initialize the pool with  workers """
        my_pool = QueueManager(CUtils.MAX_CHILD_PROCESSES)
        while True:
            # Wait for a connection
            CUtils.logger('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                CUtils.logger("connection from " + str(client_address))
                data = str(connection.recv(CUtils.READ_BYTES)).replace("\n", "")
                CUtils.logger('received data ' + data)
                response = 'OK'
                CUtils.logger('send response ' + str(response))
                connection.sendall(response)
                CUtils.logger('sent default response %s' % str(response))
                connection.close()
                CUtils.logger('Closed connection, now working on data...')
                # Close immediately to prevent Socket Blocking
                my_pool.add_task(self.create_task, data)
                my_pool.wait_completion()
            except Exception, ex:
                CUtils.logger("Exception occurred %s, continue waiting for new connection" % str(ex))
                if connection is not None:
                    connection.close()

    # function to start the service process
    def start(self):
        try:
            master = Thread(target=self.run)
            master.start()
        except Exception, er:
            self.die('unable to create main thread')

# Initialize the service
def run_service():
    pusher = Parent()
    pusher.start()

# Important: the modules should not execute code
# when they are imported
if __name__ == '__main__':
    run_service()
