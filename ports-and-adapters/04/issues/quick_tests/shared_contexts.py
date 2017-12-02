import uuid
from .adapters import FakeUnitOfWork
from issues.domain.model import Issue, IssueReporter
from issues.domain.messages import IssuePriority


class With_an_empty_unit_of_work:

    def given_a_unit_of_work(self):
        self.uow = FakeUnitOfWork()


class With_a_new_issue(With_an_empty_unit_of_work):

    def given_a_new_issue(self):
        reporter = IssueReporter('John', 'john@example.org')
        self.issue_id = uuid.uuid4()
        self.issue = Issue(self.issue_id, reporter, 'how do I even?')
        self.uow.issues.add(self.issue)


class With_a_triaged_issue(With_a_new_issue):

    def given_a_triaged_issue(self):
        self.issue.triage(IssuePriority.Low, 'uncategorised')


class With_assigned_issue(With_a_triaged_issue):

    assigned_by = 'fred@example.org'
    assigned_to = 'mary@example.org'

    def given_an_assigned_issue(self):
        self.issue.assign(assigned_to, assigned_by)
