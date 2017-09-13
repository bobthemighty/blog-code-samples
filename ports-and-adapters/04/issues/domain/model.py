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


    def __init__(self, issue_id:UUID, reporter: IssueReporter, description: str) -> None:
        self.id = issue_id
        self.description = description
        self.reporter = reporter
        self.state = Issue.State.AwaitingTriage
