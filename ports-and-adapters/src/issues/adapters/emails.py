def send_to_stdout(self, recipient, sender, subject, body):
    print(
        "Sending email to {to} from {sender}\nsubject:{subject}\n{body}".format(
            to=recipient, sender=sender, body=body, subject=subject))
