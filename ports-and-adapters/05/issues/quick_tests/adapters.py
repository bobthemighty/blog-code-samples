from collections import namedtuple

from issues.domain.ports import IssueLog, UnitOfWorkManager, UnitOfWork
from issues.domain.emails import EmailSender


class FakeIssueLog(IssueLog):

    def __init__(self):
        self.issues = []

    def add(self, issue):
        self.issues.append(issue)

    def _get(self, id):
        for issue in self.issues:
            if issue.id == id:
                return issue

    def __len__(self):
        return len(self.issues)

    def __getitem__(self, idx):
        return self.issues[idx]


class FakeUnitOfWork(UnitOfWork, UnitOfWorkManager):

    def __init__(self):
        self._issues = FakeIssueLog()

    def start(self):
        self.was_committed = False
        self.was_rolled_back = False
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.exn_type = type
        self.exn = value
        self.traceback = traceback

    def commit(self):
        self.was_committed = True

    def rollback(self):
        self.was_rolled_back = True

    @property
    def issues(self):
        return self._issues


class FakeEmailSender(EmailSender):

    sent_mail = namedtuple('fakes_sent_mail',
                           ['recipient', 'sender', 'subject', 'body'])

    def __init__(self):
        self.sent = []

    def _do_send(self, recipient, sender, subject, body):
        self.sent.append(self.sent_mail(recipient, sender, subject, body))


class FakeViewBuilder:

    def __init__(self, view_model):
        self.view_model = view_model

    def fetch(self, id):
        return self.view_model
