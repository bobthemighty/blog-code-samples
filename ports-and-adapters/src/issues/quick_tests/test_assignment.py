import uuid

from .adapters import FakeUnitOfWork, FakeEmailSender, FakeViewBuilder
from .shared_contexts import With_a_triaged_issue
from .matchers import have_raised

from issues.services import (AssignIssueHandler, IssueAssignedHandler,
                             PickIssueHandler)
from issues.domain.messages import (AssignIssueCommand, IssueAssignedToEngineer,
                                    IssueReassigned, IssueState, IssuePriority,
                                    PickIssueCommand)
from issues.domain.model import Issue, IssueReporter

from expects import expect, have_len, equal, be_true


class When_assigning_an_issue(With_a_triaged_issue):

    assigned_to = 'percy@example.org'
    assigned_by = 'norman@example.org'

    def because_we_assign_the_issue(self):
        handler = AssignIssueHandler(self.uow)
        cmd = AssignIssueCommand(self.issue_id, self.assigned_to,
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
        expect(self.issue).to(
            have_raised(
                IssueAssignedToEngineer(self.issue_id, self.assigned_to,
                                        self.assigned_by)))


class When_picking_an_issue(With_a_triaged_issue):

    picked_by = 'percy@example.org'

    def because_we_pick_the_issue(self):
        handler = PickIssueHandler(self.uow)
        cmd = PickIssueCommand(self.issue_id, self.picked_by)

        handler.handle(cmd)

    def the_issue_should_be_assigned_to_percy(self):
        expect(self.issue.assignment.assigned_to).to(equal(self.picked_by))

    def the_issue_should_be_ready_for_work(self):
        expect(self.issue.state).to(equal(IssueState.ReadyForWork))

    def it_should_have_committed_the_unit_of_work(self):
        expect(self.uow.was_committed).to(be_true)

    def it_should_not_have_raised_issue_assigned(self):
        expect(self.issue.events).to(have_len(0))


class When_reassigning_an_issue(With_a_triaged_issue):

    assigned_by = 'george@example.org'
    assigned_to = 'fred@example.org'

    new_assigned_to = 'percy@example.org'
    new_assigned_by = 'norman@example.org'

    def given_an_assigned_issue(self):
        self.issue.assign(self.assigned_to, self.assigned_by)

    def because_we_assign_the_issue(self):
        handler = AssignIssueHandler(self.uow)
        cmd = AssignIssueCommand(self.issue_id, self.new_assigned_to,
                                 self.new_assigned_by)

        handler.handle(cmd)

    def it_should_have_raised_issue_reassigned(self):
        expect(self.issue).to(
            have_raised(IssueReassigned(self.issue_id, self.assigned_to)))


class When_an_issue_is_assigned:

    issue_id = uuid.uuid4()
    assigned_to = 'barry@example.org'
    assigned_by = 'helga@example.org'

    def given_a_view_model_and_emailer(self):
        self.view_builder = FakeViewBuilder({
            'description':
            'a bad thing happened',
            'reporter_email':
            'reporter@example.org',
            'reported_name':
            'Reporty McReportface'
        })

        self.emailer = FakeEmailSender()

    def because_we_raise_issue_assigned(self):
        evt = IssueAssignedToEngineer(self.issue_id, self.assigned_to,
                                      self.assigned_by)

        handler = IssueAssignedHandler(self.view_builder, self.emailer)
        handler.handle(evt)

    def it_should_send_an_email(self):
        expect(self.emailer.sent).to(have_len(1))

    def it_should_have_the_correct_subject(self):
        expect(self.emailer.sent[0].subject).to(
            equal('Hi barry@example.org - you\'ve been assigned an issue'))

    def it_should_be_to_the_correct_recipient(self):
        expect(self.emailer.sent[0].recipient).to(equal(self.assigned_to))
