from issues.domain.model import Issue
from issues.domain.commands import ReportIssueCommand
from issues.services import ReportIssueHandler
from issues.adapters.orm import SqlAlchemy

from expects import expect, equal, have_len

class When_we_load_a_persisted_issue:

    def given_a_database_containing_an_issue(self):

        self.db = SqlAlchemy('sqlite://')
        self.db.configure_mappings()
        self.db.recreate_schema()

        cmd = ReportIssueCommand(
               'fred',
               'fred@example.org',
               'forgot my password again')
        handler = ReportIssueHandler(self.db.unit_of_work_manager)
        handler.handle(cmd)

    def because_we_load_the_issues(self):
        self.issues = self.db.get_session().query(Issue).all()

    def we_should_have_loaded_a_single_issue(self):
        expect(self.issues).to(have_len(1))

    def it_should_have_the_correct_description(self):
        expect(self.issues[0].description).to(equal('forgot my password again'))

    def it_should_have_the_correct_reporter_details(self):
        expect(self.issues[0].reporter.name).to(equal('fred'))

    def it_should_have_the_correct_reporter_details(self):
        expect(self.issues[0].reporter.email).to(equal('fred@example.org'))
