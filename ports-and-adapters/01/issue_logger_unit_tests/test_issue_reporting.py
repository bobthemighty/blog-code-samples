from .adapters import FakeIssueLog
from issue_logger_app_services.handlers import ReportIssueHandler
from issue_logger_model.commands import ReportIssueCommand

from expects import expect, have_len, equal


email = "bob@example.org"
name = "bob"
desc = "My mouse won't move"


class When_reporting_an_issue:

    def given_an_empty_issue_log(self):
        self.issues = FakeIssueLog()

    def because_we_report_a_new_issue(self):
        handler = ReportIssueHandler(self.issues)
        cmd = ReportIssueCommand(name, email, desc)

        handler(cmd)

    def the_handler_should_have_created_a_new_issue(self):
        expect(self.issues).to(have_len(1))

    def it_should_have_recorded_the_issuer(self):
        expect(self.issues[0].reporter.name).to(equal(name))
        expect(self.issues[0].reporter.email).to(equal(email))

    def it_should_have_recorded_the_description(self):
        expect(self.issues[0].description).to(equal(desc))
