import uuid

from .adapters import FakeUnitOfWork
from issues.domain.messages import ReportIssue, IssueState, IssuePriority
from issues.domain.model import Issue
from issues.services import report_issue

from expects import expect, have_len, equal, be_true

email = "bob@example.org"
name = "bob"
desc = "My mouse won't move"
id = uuid.uuid4()


class When_reporting_an_issue:

    def given_an_empty_unit_of_work(self):
        self.uow = FakeUnitOfWork()

    def because_we_report_a_new_issue(self):
        cmd = ReportIssue(id, name, email, desc)

        report_issue(lambda: self.uow, cmd)

    def the_handler_should_have_created_a_new_issue(self):
        expect(self.uow.issues).to(have_len(1))

    def it_should_have_recorded_the_id(self):
        expect(self.uow.issues[0].id).to(equal(id))

    def it_should_be_awaiting_triage(self):
        expect(self.uow.issues[0].state).to(equal(IssueState.AwaitingTriage))

    def it_should_have_recorded_the_issuer(self):
        expect(self.uow.issues[0].reporter.name).to(equal(name))
        expect(self.uow.issues[0].reporter.email).to(equal(email))

    def it_should_have_recorded_the_description(self):
        expect(self.uow.issues[0].description).to(equal(desc))

    def it_should_have_committed_the_unit_of_work(self):
        expect(self.uow.was_committed).to(be_true)
