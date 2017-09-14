import abc
from uuid import UUID
from .messages import (
        IssueState,
        IssuePriority,
        IssueReassigned,
        IssueAssignedToEngineer
    )

class IssueReporter:

    def __init__(self, name:str, email:str) -> None:
        self.name = name
        self.email = email


class Issue:

    def __init__(self, issue_id:UUID, reporter: IssueReporter, description: str) -> None:
        self.id = issue_id
        self.description = description
        self.reporter = reporter
        self.state = IssueState.AwaitingTriage
        self.events = []
        self.assigned_to = None
        self.assigned_by = None

    def triage(self, priority: IssuePriority, category: str) -> None:
        self.priority = priority
        self.category = category
        self.state = IssueState.AwaitingAssignment

    def _was_reassigned(self, previous):
        if previous is None:
            return False
        if previous == self.assigned_to:
            return False
        return True

    def assign(self, assigned_to, assigned_by):
        previous_assignee = self.assigned_to

        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.state = IssueState.ReadyForWork

        if self._was_reassigned(previous_assignee):
            self.events.append(IssueReassigned(self.id, previous_assignee))

        self.events.append(IssueAssignedToEngineer(
            self.id,
            self.assigned_to,
            self.assigned_by
        ))
