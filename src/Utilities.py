# Author    : kim kiogora <kimkiogora@gmail.com>
# Usage     : Library with various functions
# Version   : 1.0
# Since     : 28 June 2015
import sys
import logging
import ConfigParser
import imp
import os

class CUtility:
    # Global dynamic variables [ data from external XML configs will be stored in this variables ]
    MAX_WAIT_TIME = 3600*24
    READ_BYTES = 1024
    GAT_PORT = ''
    CONFIG_FILE = "conf/props.ini"
    SERVICES_CONFIG_FILE = "conf/service_configs.ini"
    MAIL_PLUGIN = "plugins/Mail/SendMail.py"
    SMS_PLUGIN = "plugins/SMS/SMSGateway.py"
    GRAPHITE_SERVER = ''
    GRAPHITE_PORT = ''
    ALERT = ''
    ALERT_EVENTS = ''
    ALERT_TYPES = ''
    ALERT_MOBILE_CONTACTS = ''
    ALERT_EMAIL_CONTACTS = ''
    MAX_CHILD_PROCESSES = 5
    WATCH_SERVICES = ''
    FAILED_LOG_FILE = ''
    ALERT_HISTORY_FILE = 'alerts_history.txt'
    LOG_FILE = "/var/log/applications/GraphiteThresholdAlerter.log"

    infoLog = logging.getLogger('GraphiteThresholdAlerter')
    logging.basicConfig(level=logging.INFO, format="%(asctime)s|%(levelname)s|%(message)s",
                        filename=LOG_FILE, filemode='a')

    def load_properties(self):
        self.logger('Loading properties...')
        try:
            self.GAT_PORT = int(self.get_property('General', self.CONFIG_FILE, 'GAT_PORT'))
            self.GRAPHITE_SERVER = self.get_property('General', self.CONFIG_FILE, 'GRAPHITE_SERVER')
            self.GRAPHITE_PORT = int(self.get_property('General', self.CONFIG_FILE, 'GRAPHITE_PORT'))
            self.ALERT = self.get_property('General', self.CONFIG_FILE, 'ALERT')
            self.ALERT_EVENTS = self.get_property('General', self.CONFIG_FILE, 'ALERT_EVENTS')
            self.ALERT_TYPES = self.get_property('General', self.CONFIG_FILE, 'ALERT_TYPES')
            self.ALERT_MOBILE_CONTACTS = self.get_property('General', self.CONFIG_FILE, 'ALERT_MOBILE_CONTACTS')
            self.ALERT_EMAIL_CONTACTS = self.get_property('General', self.CONFIG_FILE, 'ALERT_EMAIL_CONTACTS')
            self.MAX_CHILD_PROCESSES = int(self.get_property('General', self.CONFIG_FILE, 'MAX_CHILD_PROCESSES'))
            self.WATCH_SERVICES = self.get_property('General', self.CONFIG_FILE, 'WATCH_SERVICES')
            self.FAILED_LOG_FILE = self.get_property('General', self.CONFIG_FILE, 'FAILED_LOG_FILE')
            # Done loading properties...
            self.logger('All properties loaded.')
        except:
            self.infoLog.error('Exception occurred while loading properties...')
            self.die('Loading properties failed...')

    def die(self, reason):
        self.logger('Exiting, *reason => ' + reason)
        sys.exit()

    def get_property(self, category, config_file, key):
        prop = ''
        try:
            config = ConfigParser.ConfigParser()
            config.read(config_file)
            prop = config.get(category, key)
            self.logger('Loaded property { ' + key + ' = ' + prop + ' }')
        except:
            return prop
        return prop

    def logger(self, message):
        self.infoLog.info(' %s ' % message)

    def load_plugin(self, path, plugin_name):
        mod_name, file_ext = os.path.splitext(os.path.split(path)[-1])
        py_mod = imp.load_source(mod_name, path)

        if hasattr(py_mod, plugin_name):
            my_class = getattr(py_mod, plugin_name)()
            return my_class
