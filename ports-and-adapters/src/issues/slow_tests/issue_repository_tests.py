from issues.domain.ports import MessageBus
from issues.domain.model import Issue
from issues.domain.messages import ReportIssueCommand
from issues.adapters.orm import SqlAlchemy
from issues.adapters.views import IssueViewBuilder

from issues.adapters import config

import uuid

from expects import expect, equal, have_len


class When_we_load_a_persisted_issue:

    issue_id = uuid.uuid4()

    def given_a_database_containing_an_issue(self):

        cmd = ReportIssueCommand(self.issue_id, 'fred', 'fred@example.org',
                                 'forgot my password again')
        bus = config.container.resolve(MessageBus)
        bus.handle(cmd)

    def because_we_load_the_issues(self):
        view_builder = config.container.resolve(IssueViewBuilder)
        self.issue = view_builder.fetch(self.issue_id)

    def it_should_have_the_correct_description(self):
        expect(self.issue['id']).to(equal(self.issue_id))

    def it_should_have_the_correct_description(self):
        expect(self.issue['description']).to(equal('forgot my password again'))

    def it_should_have_the_correct_reporter_details(self):
        expect(self.issue['reporter_name']).to(equal('fred'))

    def it_should_have_the_correct_reporter_details(self):
        expect(self.issue['reporter_email']).to(equal('fred@example.org'))
