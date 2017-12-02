import abc
from typing import NamedTuple, NewType, Dict, Any
from jinja2 import Template

EmailAddress = NewType('email', str)
default_from_addr = EmailAddress('issues@example.org')
TemplateData = Dict[str, Any]


class MailTemplate(NamedTuple):
    subject: Template
    body: Template


class MailRequest(NamedTuple):
    template: MailTemplate
    from_addr: EmailAddress
    to_addr: EmailAddress


IssueAssignedToMe = MailTemplate(
    subject=Template("Hi {{assigned_to}} - you've been assigned an issue"),
    body=Template("{{description}}"))


class EmailSender:

    def __init__(self, send):
        self._send = send

    def send(self, request: MailRequest, data: TemplateData):
        self._send(request.to_addr, request.from_addr,
                   request.template.subject.render(data),
                   request.template.body.render(data))
