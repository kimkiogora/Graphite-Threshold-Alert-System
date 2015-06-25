__author__ = "kim"
__date__ = "$Jul, 2015 11:58:40 AM$"
import sys
import logging
import ConfigParser


class CUtility:
    # Global dynamic variables [ data from external XML configs will be stored in this variables ]
    CONFIG_FILE = "conf/props.ini"
    ALERT = ''
    ALERT_EVENTS = ''
    ALERT_TYPES = ''
    ALERT_MOBILE_CONTACTS = ''
    ALERT_EMAIL_CONTACTS = ''
    MAX_CHILD_PROCESSES = 5
    WATCH_SERVICES = ''
    FAILED_LOG_FILE = ''
    LOG_FILE = "/var/log/applications/GraphiteThresholdAlerter.log"

    infoLog = logging.getLogger('GraphiteThresholdAlerter')
    logging.basicConfig(level=logging.INFO, format= \
        "%(asctime)s - %(levelname)s - %(message)s", filename=LOG_FILE, filemode='a')

    def load_properties(self):
        self.logger('Loading properties...')
        try:
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
            self.logger('Loaded required property { ' + key + ' = ' + prop + ' }')
        except:
            return prop
        return prop

    def logger(self, message):
        self.infoLog.info(' %s ' % message)
