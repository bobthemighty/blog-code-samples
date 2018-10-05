import abc
from uuid import UUID
from .messages import (IssueState, IssuePriority, IssueReassigned,
                       IssueAssignedToEngineer)


class IssueReporter:

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email


class Assignment:

    def __init__(self, assigned_to, assigned_by):
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by

    def is_reassignment_from(self, other):
        if other is None:
            return False
        if other.assigned_to == self.assigned_to:
            return False
        return True


class Issue:

    def __init__(self, issue_id: UUID, reporter: IssueReporter,
                 description: str) -> None:
        self.id = issue_id
        self.description = description
        self.reporter = reporter
        self.state = IssueState.AwaitingTriage
        self.events = []
        self._assignments = []

    @property
    def assignment(self):
        if len(self._assignments) == 0:
            return None
        return self._assignments[-1]

    def triage(self, priority: IssuePriority, category: str) -> None:
        self.priority = priority
        self.category = category
        self.state = IssueState.AwaitingAssignment

    def assign(self, assigned_to, assigned_by=None):
        previous_assignment = self.assignment
        assigned_by = assigned_by or assigned_to

        self._assignments.append(Assignment(assigned_to, assigned_by))

        self.state = IssueState.ReadyForWork

        if self.assignment.is_reassignment_from(previous_assignment):
            self.events.append(
                IssueReassigned(self.id, previous_assignment.assigned_to))

        if assigned_to != assigned_by:
            self.events.append(
                IssueAssignedToEngineer(self.id, assigned_to, assigned_by))
