import uuid

from .shared_contexts import With_a_new_issue

from issues.services import TriageIssueHandler
from issues.domain.messages import TriageIssueCommand, IssuePriority, IssueState
from issues.domain.model import Issue

from expects import expect, have_len, equal, be_true

class When_triaging_an_issue (With_a_new_issue):

    issue_id = uuid.uuid4()
    category = 'training'
    priority = IssuePriority.Low

    def because_we_triage_the_issue(self):
        handler = TriageIssueHandler(self.uow)
        cmd = TriageIssueCommand(self.issue_id, self.category, self.priority)

        handler.handle(cmd)

    def the_issue_should_have_a_priority_set(self):
        expect(self.issue.priority).to(equal(IssuePriority.Low))

    def the_issue_should_have_been_categorised(self):
        expect(self.issue.category).to(equal('training'))

    def the_issue_should_be_awaiting_assignment(self):
        expect(self.issue.state).to(equal(IssueState.AwaitingAssignment))

    def it_should_have_committed_the_unit_of_work(self):
        expect(self.uow.was_committed).to(be_true)


