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
import subprocess
import os

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
                CUtils.logger("connection from " + str(client_address))
                data = str(connection.recv(1024))
                CUtils.logger('received ' + data)
                response = 'OK'
                CUtils.logger('Send response ' + str(response))
                connection.sendall(response)
                CUtils.logger('Sent')

                "Work on the message"
                CUtils.logger('Check on how message should be filtered')

                "Monitor value as such Service-X-Failure-Rate_37_1435311284"
                if '_' in data:
                    data_array = data.split('_')
                    service_monitor = data_array[0]
                    gat_size = data_array[1]
                    time_value = data_array[2]

                    request = service_monitor+" "+str(gat_size)+" "+str(time_value)

                    CUtils.logger("Found service"+service_monitor+", count_value "
                                  +gat_size+", time_value "+time_value)

                    CUtils.logger("Checking threshold monitoring list...")

                    if CUtils.WATCH_SERVICES is not None:
                        w_list = []
                        if "|" not in CUtils.WATCH_SERVICES:
                            w_list.append(CUtils.WATCH_SERVICES)
                        else:
                            for x in CUtils.WATCH_SERVICES.split("|"):
                                w_list.append(x)

                        if service_monitor not in w_list:
                            CUtils.logger("Service not found in threshold monitoring list...")
                            CUtils.logger("Rerouting request { "+request+" } to Graphite...")
                            if self.push_via_netcat(request):
                                CUtils.logger("Request routed")
                            else:
                                CUtils.logger("Request routing failed")
                            CUtils.logger("Request routed")
                            return
                        CUtils.logger("Service found in threshold monitoring list...")
                        monitor_threshold_value = int(
                            CUtils.get_property(service_monitor, CUtils.SERVICES_CONFIG_FILE, 'THRESHOLD'))

                        CUtils.logger("Applying filter rules for alerts...")
                        if gat_size >= monitor_threshold_value:
                            CUtils.logger("Threshold value surpassed. Time to alert people...")
                            alert_message = CUtils.get_property(
                                service_monitor, CUtils.SERVICES_CONFIG_FILE, 'MESSAGE')
                            CUtils.logger("Sending alert "+ str(alert_message))

                            "Put some check so we do not send the alert many times"

                            CUtils.logger("Sent alert")
                        else:
                            CUtils.logger("Service is operating normally")
                    else:
                        CUtils.logger("Threshold monitoring list has no services configured...")
                        CUtils.logger("Rerouting request { "+request+" } to Graphite...")
                        if self.push_via_netcat(request):
                            CUtils.logger("Request routed")
                        else:
                            CUtils.logger("Request routing failed")
                    print data_array
            finally:
                # Clean up the connection
                connection.close()

    def push_via_netcat(self,command):
        status = False
        try:
            subprocess.Popen(["/bin/sh", "-c",str(command)+"|nc "
                                + str(CUtils.GRAPHITE_SERVER)+" "+str(CUtils.GRAPHITE_PORT)])
            status = True
        except Exception, e:
            CUtils.logger("Exception during push_via_netcat call, reason "+str(e.message))
            "Do sth like a save to file and retry using a back-off algorithm"
            pass
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
