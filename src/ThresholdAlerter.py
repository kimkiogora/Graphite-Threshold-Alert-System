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
import subprocess
import os

global queue
global watch_queue

watch_queue = []

CUtils = CUtility()

# The class itself
class Parent:
    mypool = None

    # An empty constructor
    def __init__(self):
        CUtils.logger('Locating config file = ' + CUtils.CONFIG_FILE + '...')
        if os.path.exists(CUtils.CONFIG_FILE):
            CUtils.logger('Found config file = ' + CUtils.CONFIG_FILE + '...')
            CUtils.load_properties()
        else:
            CUtils.infoLog.error('Config file = ' + CUtils.CONFIG_FILE + ' not found, exiting...')
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
        task = Task(data)
        task.processData()

    def get_matching_config_service(self, key, service_list):
        for service_id in service_list:
            if str(service_id).lower() == key.lower():
                return service_id

    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('localhost', CUtils.GAT_PORT)
        CUtils.logger('starting up on %s port %s' % server_address)
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(CUtils.MAX_CHILD_PROCESSES)
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

                "Work on the message"
                CUtils.logger('check on how message should be filtered')

                "Monitor value as such Service-X-Failure-Rate_37_1435311284"
                if '_' in data:
                    data_array = data.split('_')
                    error_status = ''
                    try:
                        service_monitor = data_array[0]
                    except:
                        service_monitor = None
                    try:
                        gat_size = data_array[1]
                    except:
                        gat_size = None
                    try:
                        time_value = data_array[2]
                    except:
                        time_value = None

                    if service_monitor is None:
                        CUtils.logger("Error extracting service_monitor_name. "
                                      "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                        error_status = True

                    if gat_size is None:
                        CUtils.logger("Error extracting monitor value. "
                                      "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                        error_status = True

                    if time_value is None:
                        CUtils.logger("Error extracting time series value. "
                                      "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                        error_status = True

                    if not error_status:
                        gat_size = int(gat_size)
                        request = service_monitor + " " + str(gat_size) + " " + str(time_value)
                        CUtils.logger("found service " + service_monitor + ", count_value "
                                      + str(gat_size) + ", time_value " + time_value)
                        CUtils.logger("checking threshold monitoring list...")
                        if CUtils.WATCH_SERVICES is not None:
                            w_list = []
                            if "|" not in CUtils.WATCH_SERVICES:
                                w_list.append(CUtils.WATCH_SERVICES)
                            else:
                                for x in CUtils.WATCH_SERVICES.split("|"):
                                    w_list.append(x)

                            CUtils.logger("service comparison string "+service_monitor+" list " + str(w_list))

                            service_monitor_match = self.get_matching_config_service(service_monitor, w_list)

                            if service_monitor_match is None:
                                CUtils.logger("service not found in threshold monitoring list...")
                                CUtils.logger("rerouting request { " + request + " } to Graphite...")
                                if self.push_via_netcat(request):
                                    CUtils.logger("request routed")
                                else:
                                    CUtils.logger("request routing failed")
                            else:
                                service_monitor = service_monitor_match
                                CUtils.logger("service found in threshold monitoring list...")
                                monitor_threshold_value = int(
                                    CUtils.get_property(service_monitor, CUtils.SERVICES_CONFIG_FILE, 'THRESHOLD'))
                                CUtils.logger("applying filter rules for alerts...")
                                if gat_size >= monitor_threshold_value:
                                    CUtils.logger("threshold value surpassed. Time to alert people...")
                                    alert_message = CUtils.get_property(
                                        service_monitor, CUtils.SERVICES_CONFIG_FILE, 'MESSAGE')
                                    CUtils.logger("sending alert " + str(alert_message))
                                    "Put some check so we do not send alert many times"

                                    sent_alerts = self.load_sent_alerts(CUtils.ALERT_HISTORY_FILE)
                                    alert_types = CUtils.ALERT_TYPES.split("|")

                                    if sent_alerts is None:
                                        CUtils.logger("no alerts in history file")
                                        if "MAIL" in alert_types:
                                            self.send_mail(service_monitor, alert_message)
                                        if "SMS" in alert_types:
                                            self.send_sms(service_monitor, alert_message)
                                    else:
                                        CUtils.logger("alerts in history file %s" % str(sent_alerts))
                                        formatted_msg = service_monitor+'_'+alert_message
                                        if "MAIL" in alert_types:
                                            if not self.check_alert_sent(formatted_msg, 'MAIL',sent_alerts):
                                                self.send_mail(service_monitor, alert_message)
                                        if "SMS" in alert_types:
                                            if not self.check_alert_sent(formatted_msg, 'SMS', sent_alerts):
                                                self.send_sms(service_monitor, alert_message)
                                else:
                                    CUtils.logger("threshold below send alert value")
                                    CUtils.logger("rerouting request { " + request + " } to Graphite...")
                                    if self.push_via_netcat(request):
                                        CUtils.logger("request routed")
                                    else:
                                        CUtils.logger("request routing failed")
                        else:
                            CUtils.logger("threshold monitoring list has no services configured...")
                            CUtils.logger("rerouting request { " + request + " } to Graphite...")
                            if self.push_via_netcat(request):
                                CUtils.logger("request routed")
                            else:
                                CUtils.logger("request routing failed")
                else:
                    CUtils.logger("Expected data in format [ MONITORING-ID_COUNT_TIMESTAMP ]")
            finally:
                # Clean up the connection
                CUtils.logger("close connection and wait for a new one")
                connection.close()

    def load_sent_alerts(self, filex):
        stack = []
        try:
            f = open(filex)
            for line in f:
                if line != '' or line is not None:
                    stack.append(line.replace("\n", ''))
        except:
            pass
        return stack

    def push_to_queue(self, service, data):
        data = service + "_" +data+"_"+str(time.time())
        watch_queue.append(data)
        self.write_alert_history(data)

    def write_alert_history(self, data):
        CUtils.logger('Appending alert history..')
        try:
            f = open(CUtils.ALERT_HISTORY_FILE, 'a')
            f.write(data)
            f.write('\n')
            f.close()
            CUtils.logger('Appended alert history.')
        except:
            e_value = sys.exc_info()[1]
            CUtils.logger("Error %s writing file" % str(e_value))

    def check_alert_sent(self, alert, alert_type, alert_queue):
        CUtils.logger("confirm if sms => %s was sent" % alert)
        sent_status = False
        if len(alert_queue) <= 0 or alert_queue is None:
            CUtils.logger("nothing in sent queue, sending...")
            sent_status = False
        else:
            try:
                for al in alert_queue:
                    alert_data = str(al).split("_")
                    my_alert = alert_data[1]
                    my_type = alert_data[2]
                    formatted_msg = alert_data[0] + "_" + my_alert
                    if str(alert) == str(formatted_msg) and my_type == alert_type:
                        last_send = float(alert_data[3])
                        now = time.time()
                        sec_elapsed = now-last_send
                        if sec_elapsed > CUtils.MAX_WAIT_TIME:
                            CUtils.logger("resending alert as max wait time has passed and issue seems persistent...")
                            sent_status = False
                        else:
                            CUtils.logger("alert already sent %d sec(s) ago. Nothing to do" % float(sec_elapsed))
                            sent_status = True
                        return sent_status
            except:
                sent_status = True
        return sent_status

    def send_mail(self, service, alert_message):
        address_list = CUtils.ALERT_EMAIL_CONTACTS.split("|")
        if len(address_list) > 0:
            new_address_list = ', '.join(address_list)
            my_class = CUtils.load_plugin(CUtils.MAIL_PLUGIN, 'PMailer')
            if my_class is not None:
                try:
                    s_status = my_class.process(alert_message, new_address_list, CUtils.infoLog)
                    if s_status:
                        CUtils.logger("mail alert has been sent")
                        self.push_to_queue(service, alert_message+"_MAIL")
                    else:
                        CUtils.logger("mail alert was not sent")
                except:
                    e_value = sys.exc_info()[1]
                    CUtils.logger("error %s during plugin execution call" % str(e_value))
            else:
                CUtils.logger("plugin load failed")

    def send_sms(self, service, alert_message):
        sms_list = CUtils.ALERT_MOBILE_CONTACTS.split("|")
        if len(sms_list) > 0:
            new_sms_list = ', '.join(sms_list)
            my_class = CUtils.load_plugin(CUtils.SMS_PLUGIN, 'SMSHelper')
            if my_class is not None:
                try:
                    s_status = my_class.process(alert_message, new_sms_list, CUtils.infoLog)
                    if s_status:
                        CUtils.logger("SMS alert has been sent")
                        self.push_to_queue(service, alert_message+"_SMS")
                    else:
                        CUtils.logger("SMS alert was not sent")
                except:
                    e_value = sys.exc_info()[1]
                    CUtils.logger("error %s during plugin execution call" % str(e_value))
            else:
                CUtils.logger("plugin load failed")

    def push_via_netcat(self, command):
        global status
        try:
            subprocess.Popen(["/bin/sh", "-c", "echo "+str(command) + "|nc "
                              + str(CUtils.GRAPHITE_SERVER) + " " + str(CUtils.GRAPHITE_PORT)])
            status = True
        except Exception, e:
            CUtils.logger("exception during push_via_netcat call, reason " + str(e.message))
            "Do sth like a save to file and retry using a back-off algorithm"
            status = False
        return status

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
