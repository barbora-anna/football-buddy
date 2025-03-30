import smtplib
import logging
from email.message import EmailMessage


log = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, host, port, sender_email, sender_password):
        self.host = host
        self.port = port
        self.sender_email = sender_email
        self._password = sender_password


    def format_email(self, subject, receiver_email, content, is_html=False):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg.set_content(content)

        if is_html:
            msg.add_alternative(content, subtype='html')

        return msg

    def send_email(self, msg):
        try:
            with smtplib.SMTP_SSL(self.host, self.port) as server:
                log.debug("Connecting to email server...")
                server.login(self.sender_email, self._password)
                log.debug("Logged in successfully!")
                server.send_message(msg)
                log.info("Email sent successfully!")
        except smtplib.SMTPAuthenticationError:
            err_msg = "Authentication failed. Check your email/password."
            log.error(err_msg)
            raise Exception(err_msg)
        except Exception as e:
            err_msg = f"An error occurred: {e}"
            log.error(err_msg)
            raise Exception(err_msg)





