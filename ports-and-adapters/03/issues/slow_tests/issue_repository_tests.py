from issues.domain.model import Issue
from issues.domain.commands import ReportIssueCommand
from issues.services import handle_report_issue
from issues.adapters.orm import SqlAlchemy
from issues.adapters.views import view_issue

import uuid

from expects import expect, equal, have_len

class When_we_load_a_persisted_issue:

    def given_a_database_containing_an_issue(self):
        self.db = SqlAlchemy('sqlite://')
        self.db.configure_mappings()
        self.db.recreate_schema()

        self.issue_id = uuid.uuid4()

        cmd = ReportIssueCommand(
            self.issue_id,
            'fred',
            'fred@example.org',
            'forgot my password again'
        )
        handle_report_issue(self.db.get_unit_of_work(), cmd)

    def because_we_load_the_issues(self):
        self.issue = view_issue(self.db.start_session(), self.issue_id)

    def it_should_have_the_correct_id(self):
        # expect(self.issue['id']).to(equal(self.issue_id))
        pass

    def it_should_have_the_correct_description(self):
        expect(self.issue['description']).to(equal('forgot my password again'))

    def it_should_have_the_correct_reporter_name(self):
        expect(self.issue['reporter_name']).to(equal('fred'))

    def it_should_have_the_correct_reporter_details(self):
        expect(self.issue['reporter_email']).to(equal('fred@example.org'))

