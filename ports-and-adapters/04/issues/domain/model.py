import abc
from uuid import UUID
from .messages import IssueState, IssuePriority, IssueAssignedToEngineer

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

    def triage(self, priority: IssuePriority, category: str) -> None:
        self.priority = priority
        self.category = category
        self.state = IssueState.AwaitingAssignment

    def assign(self, assigned_to, assigned_by):
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.state = IssueState.ReadyForWork
        self.events.append(IssueAssignedToEngineer(
            self.id,
            self.assigned_to,
            self.assigned_by
        ))
