# Author    kim kiogora <kimkiogora@gmail.com>
# Usage     SMS Plugin for sending short messages / alerts
# Version   1.0
# Since     28 June 2015
import logging
#import urllib2
#import json

class SMSHelper:
  def process(self, message, receiver, log_file):
    info_log = logging.getLogger('SMSHelper')
    logging.basicConfig(level=logging.INFO, format="%(asctime)s|%(levelname)s| %(message)s", filename=log_file,
                            filemode='a')
    info_log.info(" preparing to send SMS %s alert" % str(message))
    list_of_receivers = str(receiver).split(",")
    info_log.info(" send sms to list => %s" % str(list_of_receivers))

    total = len(list_of_receivers)
    success_sends = 0

    for contact in list_of_receivers:
      info_log.info(" send sms to contact => %s" % str(contact))
      if self.get_sms_gateway_response(info_log, str(contact).replace(" ",""), message) == 'OK':
        success_sends += 1
      else:
        info_log.info(" send sms to contact %s failed" % contact)
    success_rate = (100*success_sends)/total
    if success_rate > 1:
      status = True
    
    return status
    
  def get_sms_gateway_response(self, logger, destination, message):
    logger.info(" preparing sms ...")
    'Add your EMG/SMS functionality here'
    #return 'OK'
    return 'FAIL'
    
#########################################
# Sample test
# sms_test = SMSHelper()
# sms_test.process("This is a test for Graphana",
#                 "mobile number A,mobile number B", "/var/log/applications/GraphiteThresholdAlerter.log")

