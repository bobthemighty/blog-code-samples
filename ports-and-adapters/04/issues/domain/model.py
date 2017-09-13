import abc
from enum import Enum
from uuid import UUID

class IssueReporter:

    def __init__(self, name:str, email:str) -> None:
        self.name = name
        self.email = email


class Issue:

    class State(Enum):
        AwaitingTriage = 0
        AwaitingAssignment = 1

    class Priority(Enum):
        NotPrioritised = 0
        Low = 1
        Normal = 2
        High = 3
        Urgent = 4


    def __init__(self, issue_id:UUID, reporter: IssueReporter, description: str) -> None:
        self.id = issue_id
        self.description = description
        self.reporter = reporter
        self.state = Issue.State.AwaitingTriage

    def triage(self, priority: Priority, category: str) -> None:
        self.priority = priority
        self.category = category
        self.state = Issue.State.AwaitingAssignment
