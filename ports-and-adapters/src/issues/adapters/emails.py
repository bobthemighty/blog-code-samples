import logging
from typing import Dict, Any
from issues.domain.emails import EmailSender, MailRequest


class LoggingEmailSender(EmailSender):

    def _do_send(self, recipient, sender, subject, body):
        print("Sending email to {to} from {sender}\nsubject:{subject}\n{body}".
              format(to=recipient, sender=sender, body=body, subject=subject))
