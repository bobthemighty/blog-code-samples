import abc

class IssueReporter:

    def __init__(self, name:str, email:str) -> None:
        self.name = name
        self.email = email


class Issue:
    def __init__(self, reporter: IssueReporter, description: str) -> None:
        self.description = description
        self.reporter = reporter


class IssueLog(abc.ABC):

    @abc.abstractmethod
    def add(self, issue: Issue) -> None:
        pass
