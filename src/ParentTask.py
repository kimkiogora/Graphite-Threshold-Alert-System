#@Author    : Kim Kiogora	<kimkkiogora@gmail.com>
#@Usage     : Alerts for graphite
#@Version   : 1.0
#@Since     : 28 June 2015
import subprocess
import time
import sys
class Task:
    # variables
    my_data = None
    c_utils = None

    def __init__(self, data, c_utility):
        self.my_data = data
        self.c_utils = c_utility

    def process_data(self):
        """Work on the message"""
        self.c_utils.logger("check on how message should be filtered")
        "Monitor value as such Service-X-Failure-Rate_37_1435311284"
        if '_' in self.my_data:
            data_array = self.my_data.split('_')
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
                self.c_utils.logger("Error extracting service_monitor_name. "
                                    "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                error_status = True

            if gat_size is None:
                self.c_utils.logger("Error extracting monitor value. "
                                    "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                error_status = True

            if time_value is None:
                self.c_utils.logger("Error extracting time series value. "
                                    "Expected it in the format [ MONITORING-ID_COUNT_TIMESTAMP  ]")
                error_status = True

            if not error_status:
                gat_size = int(gat_size)
                request = service_monitor + " " + str(gat_size) + " " + str(time_value)
                self.c_utils.logger("found service " + service_monitor
                                    + ", count_value "+ str(gat_size)
                                    + ", time_value " + time_value)
                self.c_utils.logger("checking threshold monitoring list..." + str(self.c_utils.WATCH_SERVICES))
                if self.c_utils.WATCH_SERVICES is not None:
                    w_list = []
                    if "|" not in self.c_utils.WATCH_SERVICES:
                        w_list.append(self.c_utils.WATCH_SERVICES)
                    else:
                        for x in self.c_utils.WATCH_SERVICES.split("|"):
                            w_list.append(x)

                    self.c_utils.logger("service comparison string " + service_monitor + " list " + str(w_list))

                    service_monitor_match = self.get_matching_config_service(service_monitor, w_list)

                    if service_monitor_match is None:
                        self.c_utils.logger("service not found in threshold monitoring list...")
                        self.c_utils.logger("rerouting request { " + request + " } to Graphite...")
                        if self.push_via_netcat(request):
                            self.c_utils.logger("request routed")
                        else:
                            self.c_utils.logger("request routing failed")
                    else:
                        service_monitor = service_monitor_match
                        self.c_utils.logger("service found in threshold monitoring list...")
                        monitor_threshold_value = int(
                            self.c_utils.get_property(service_monitor, self.c_utils.SERVICES_CONFIG_FILE, 'THRESHOLD'))
                        self.c_utils.logger("applying filter rules for alerts...")
                        if gat_size >= monitor_threshold_value:
                            self.c_utils.logger("rerouting request { " + request + " } to Graphite...")
                            if self.push_via_netcat(request):
                                self.c_utils.logger("request routed")
                            else:
                                self.c_utils.logger("request routing failed")
                            self.c_utils.logger("threshold value surpassed. Time to alert people...")
                            alert_message = self.c_utils.get_property(
                                service_monitor, self.c_utils.SERVICES_CONFIG_FILE, 'MESSAGE')
                            self.c_utils.logger("sending alert " + str(alert_message))
                            "Put some check so we do not send alert many times"

                            sent_alerts = self.load_sent_alerts(self.c_utils.ALERT_HISTORY_FILE)
                            alert_types = self.c_utils.ALERT_TYPES.split("|")

                            if sent_alerts is None:
                                self.c_utils.logger("no alerts in history file")
                                if "MAIL" in alert_types:
                                    self.send_mail(service_monitor, alert_message)
                                if "SMS" in alert_types:
                                    self.send_sms(service_monitor, alert_message)
                            else:
                                self.c_utils.logger("alerts in history file %s" % str(sent_alerts))
                                formatted_msg = service_monitor + '_' + alert_message
                                if "MAIL" in alert_types:
                                    if not self.check_alert_sent(formatted_msg, 'MAIL', sent_alerts):
                                        self.send_mail(service_monitor, alert_message)
                                if "SMS" in alert_types:
                                    if not self.check_alert_sent(formatted_msg, 'SMS', sent_alerts):
                                        self.send_sms(service_monitor, alert_message)
                        else:
                            self.c_utils.logger("threshold below send alert value")
                            self.c_utils.logger("rerouting request { " + request + " } to Graphite...")
                            if self.push_via_netcat(request):
                                self.c_utils.logger("request routed")
                            else:
                                self.c_utils.logger("request routing failed")
                else:
                    self.c_utils.logger("threshold monitoring list has no services configured...")
                    self.c_utils.logger("rerouting request { " + request + " } to Graphite...")
                    if self.push_via_netcat(request):
                        self.c_utils.logger("request routed")
                    else:
                        self.c_utils.logger("request routing failed")
        else:
            self.c_utils.logger("Expected data in format [ MONITORING-ID_COUNT_TIMESTAMP ]")

    def get_matching_config_service(self, key, service_list):
        for service_id in service_list:
            if str(service_id).lower() == key.lower():
                return service_id

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

    def check_alert_sent(self, alert, alert_type, alert_queue):
        self.c_utils.logger("confirm if sms => %s was sent" % alert)
        sent_status = False
        if len(alert_queue) <= 0 or alert_queue is None:
            self.c_utils.logger("nothing in sent queue, sending...")
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
                        if sec_elapsed > self.c_utils.MAX_WAIT_TIME:
                            self.c_utils.logger("resending alert as max wait time has passed"
                                                " and issue seems persistent...")
                            sent_status = False
                        else:
                            self.c_utils.logger("alert already sent %d sec(s) ago. Nothing to do. If this issue is "
                                                "persistent, next alert will be sent after 24 hrs" % float(sec_elapsed))
                            sent_status = True
                        return sent_status
            except:
                sent_status = True
        return sent_status

    def send_mail(self, service, alert_message):
        address_list = self.c_utils.ALERT_EMAIL_CONTACTS.split("|")
        if len(address_list) > 0:
            new_address_list = ', '.join(address_list)
            my_class = self.c_utils.load_plugin(self.c_utils.MAIL_PLUGIN, 'PMailer')
            if my_class is not None:
                try:
                    s_status = my_class.process(alert_message, new_address_list, self.c_utils.infoLog)
                    if s_status:
                        self.c_utils.logger("mail alert has been sent")
                        self.push_to_queue(service, alert_message+"_MAIL")
                    else:
                        self.c_utils.logger("mail alert was not sent")
                except:
                    e_value = sys.exc_info()[1]
                    self.c_utils.logger("error %s during plugin execution call" % str(e_value))
            else:
                self.c_utils.logger("plugin load failed")

    def send_sms(self, service, alert_message):
        sms_list = self.c_utils.ALERT_MOBILE_CONTACTS.split("|")
        if len(sms_list) > 0:
            new_sms_list = ', '.join(sms_list)
            my_class = self.c_utils.load_plugin(self.c_utils.SMS_PLUGIN, 'SMSHelper')
            if my_class is not None:
                try:
                    s_status = my_class.process(alert_message, new_sms_list, self.c_utils.infoLog)
                    if s_status:
                        self.c_utils.logger("SMS alert has been sent")
                        self.push_to_queue(service, alert_message+"_SMS")
                    else:
                        self.c_utils.logger("SMS alert was not sent")
                except:
                    e_value = sys.exc_info()[1]
                    self.c_utils.logger("error %s during plugin execution call" % str(e_value))
            else:
                self.c_utils.logger("plugin load failed")

    def push_to_queue(self, service, data):
        data = service + "_" + data + "_" + str(time.time())
        self.write_alert_history(data)

    def write_alert_history(self, data):
        self.c_utils.logger('Appending alert history..')
        try:
            f = open(self.c_utils.ALERT_HISTORY_FILE, 'a')
            f.write(data)
            f.write('\n')
            f.close()
            self.c_utils.logger('Appended alert history.')
        except:
            e_value = sys.exc_info()[1]
            self.c_utils.logger("Error %s writing file" % str(e_value))

    def push_via_netcat(self, command):
        global status
        try:
            subprocess.Popen(["/bin/sh", "-c", "echo "+str(command) + "|nc "
                              + str(self.c_utils.GRAPHITE_SERVER) + " " + str(self.c_utils.GRAPHITE_PORT)])
            status = True
        except Exception, e:
            self.c_utils.logger("exception during push_via_netcat call, reason " + str(e.message))
            "Do sth like a save to file and retry using a back-off algorithm"
            status = False
        return status
