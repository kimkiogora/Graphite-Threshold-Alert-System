# Author kim kiogora <kimkiogora@gmail.com>
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class PMailer:
    password = ''
    sender = ''
    host = 'smtp.gmail.com'
    port = '465'

    def __init__(self):
        pass

    def debug(self, message):
        print message

    def process(self, message, receiver):
        """
        :type receiver: list
        """
        try:
            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Graphite Threshold Alert"
            msg['From'] = self.sender
            msg['To'] = receiver

            # Create the body of the message (a plain-text and an HTML version).
            text = "Hi!\nHow are you?\nThis is an automated alert from Grafana:\n" \
                   "Copyright (c) Alerter\n"
            html = """\
            <html>
              <head></head>
              <body>
                <p>Hello<br>
                   How are you ?<br>
                   %s
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

            self.debug("Assembled message")
            self.debug("Connecting to gmail...")

            # Send the message via local SMTP server.
            mail = smtplib.SMTP('smtp.gmail.com', 587)

            self.debug("Connected to gmail. Issue ehlo..")

            mail.ehlo()

            self.debug("Issued ehlo, starttls next...")

            mail.starttls()

            self.debug("starttls done, login....")
            mail.login(self.sender, self.password)

            self.debug("Logged in to gmail.Send mail...")

            mail.sendmail(self.sender, receiver, msg.as_string())

            self.debug("Sent mail , quit...")

            mail.quit()

            self.debug("Quit.")
        except Exception, ex:
            print ex
#Test
#mailer = PMailer()
#mailer.process("Service Y Failure Rate Threshold surpassed at Value 100 ","xxx@yahoo.com")
