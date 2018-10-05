import abc
from collections import defaultdict
from uuid import UUID
from .model import Issue


class IssueNotFoundException(Exception):
    pass


class IssueLog(abc.ABC):

    @abc.abstractmethod
    def add(self, issue: Issue) -> None:
        pass

    @abc.abstractmethod
    def _get(self, id: UUID) -> Issue:
        pass

    def get(self, id: UUID) -> Issue:
        issue = self._get(id)
        if issue is None:
            raise IssueNotFoundException()
        return issue


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


class CommandAlreadySubscribedException(Exception):
    pass


class HandlerRegistry:

    def get_handlers(self, type):
        pass


class MessageBus:

    def __init__(self, registry: HandlerRegistry):
        self.registry = registry

    def handle(self, msg):
        subscribers = self.registry.get_handlers(type(msg))
        for subscriber in subscribers:
            subscriber.handle(msg)


class IssueViewBuilder:

    @abc.abstractmethod
    def fetch(self, id):
        pass


class IssueListViewBuilder:

    @abc.abstractmethod
    def fetch(self):
        pass
