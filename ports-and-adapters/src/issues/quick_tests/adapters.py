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


sent_mail = namedtuple('fakes_sent_mail',
                       ['recipient', 'sender', 'subject', 'body'])


def fake_sender(sent):

    def send(recipient, sender, subject, body):
        sent.append(sent_mail(recipient, sent_mail, subject, body))

    return send
