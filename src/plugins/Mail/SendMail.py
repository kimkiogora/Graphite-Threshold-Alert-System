# Author    kim kiogora <kimkiogora@gmail.com>
# Usage     Mail Plugin for sending mail alerts
# Version   1.0
# Since     28 June 2015

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

class PMailer:
    password = ''
    sender = ''
    host = 'smtp.gmail.com'
    port = 587

    def __init__(self):
        pass

    def debug(self, message):
        #print message
        pass

    def process(self, message, receiver, log_file):
        global status
        info_log = logging.getLogger('PMailer')
        logging.basicConfig(level=logging.INFO, format="%(asctime)s|%(levelname)s| %(message)s",
                        filename=log_file, filemode='a')
        """
        :type receiver: list
        """
        list_of_receivers = str(receiver).split(",")
        info_log.info(" send mail to these people => %s" % str(list_of_receivers))
        try:
            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Graphite Threshold Alert"
            msg['From'] = self.sender
            msg['To'] = receiver

            # Create the body of the message (a plain-text and an HTML version).
            text = "Hi!\nThis is an automated alert from GTA System:\n" \
                   "Copyright(C) GTA System\n"
            html = """\
            <html>
              <head></head>
              <body>
                <p>Hello<br>
                   How are you ?<br>This is an automated alert from GTA System:<br>
                   %s
                   <br>Copyright (C) GTA System</br>
                </p>
              </body>
            </html>
            """ % message

            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)

            info_log.info(" Assembled message...")
            info_log.info(" Content '%s'" % message)
            info_log.info(" Connecting to GMail...")

            # Send the message via local SMTP server.
            mail = smtplib.SMTP('smtp.gmail.com', self.port)

            info_log.info(" Connected to GMail. Issue ehlo..")

            mail.ehlo()

            info_log.info(" Issued ehlo. Proceed to issue starttls next...")

            mail.starttls()

            info_log.info(" starttls issued, now logging in....")

            mail.login(self.sender, self.password)

            info_log.info(" logged in to GMail, now sending mail alert...")

            mail.sendmail(self.sender, receiver, msg.as_string())

            info_log.info(" Sent mail alert, signing out...")

            mail.quit()

            info_log.info(" Signed out.")

            status = True
        except Exception, ex:
            info_log.info(" An error occurred during send mail, error %s" % str(ex))
            status = False
        return status
