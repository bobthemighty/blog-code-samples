import abc
from .model import Issue


class IssueLog(abc.ABC):

    @abc.abstractmethod
    def add(self, issue: Issue) -> None:
        pass


class UnitOfWork(abc.ABC):

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

    @property
    @abc.abstractmethod
    def issues(self):
        pass


class UnitOfWorkManager(abc.ABC):

    @abc.abstractmethod
    def start(self) -> UnitOfWork:
        pass
