import uuid

from .adapters import FakeUnitOfWork
from .shared_contexts import With_a_triaged_issue
from .matchers import have_raised

from issues.services import AssignIssueHandler
from issues.domain.messages import (
        AssignIssueCommand,
        IssueAssignedToEngineer,
        IssueReassigned,
        IssueState,
        IssuePriority
    )
from issues.domain.model import Issue, IssueReporter

from expects import expect, have_len, equal, be_true


class When_assigning_an_issue (With_a_triaged_issue):

    assigned_to = 'percy@example.org'
    assigned_by = 'norman@example.org'

    def because_we_assign_the_issue(self):
        handler = AssignIssueHandler(self.uow)
        cmd = AssignIssueCommand(
                self.issue_id,
                self.assigned_to,
                self.assigned_by)

        handler.handle(cmd)

    def the_issue_should_be_assigned_to_percy(self):
        expect(self.issue.assignment.assigned_to).to(equal(self.assigned_to))

    def the_issue_should_have_been_assigned_by_norman(self):
        expect(self.issue.assignment.assigned_by).to(equal(self.assigned_by))

    def the_issue_should_be_ready_for_work(self):
        expect(self.issue.state).to(equal(IssueState.ReadyForWork))

    def it_should_have_committed_the_unit_of_work(self):
        expect(self.uow.was_committed).to(be_true)

    def it_should_have_raised_issue_assigned(self):
        expect(self.issue).to(have_raised(
            IssueAssignedToEngineer(
                self.issue_id,
                self.assigned_to,
                self.assigned_by
            )))


class When_reassigning_an_issue (With_a_triaged_issue):

    assigned_by = 'george@example.org'
    assigned_to = 'fred@example.org'

    new_assigned_to = 'percy@example.org'
    new_assigned_by = 'norman@example.org'

    def given_an_assigned_issue(self):
        self.issue.assign(self.assigned_to, self.assigned_by)

    def because_we_assign_the_issue(self):
        handler = AssignIssueHandler(self.uow)
        cmd = AssignIssueCommand(
                self.issue_id,
                self.new_assigned_to,
                self.new_assigned_by)

        handler.handle(cmd)

    def it_should_have_raised_issue_reassigned(self):
        expect(self.issue).to(have_raised(
            IssueReassigned(
                self.issue_id,
                self.assigned_to
            )))
