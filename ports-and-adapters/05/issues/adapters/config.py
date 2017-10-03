import inspect
import logging

from . import orm

from .emails import LoggingEmailSender

import issues.domain.messages as msg
from issues.domain import ports
from issues import services, domain, adapters
from issues.adapters import views

import punq


class PunqMessageRegistry(ports.HandlerRegistry):

    def __init__(self, container):
        self.container = container

    def get_message_type(self, type):
        try:
            for base in type.__orig_bases__:
                if base.__origin__ == services.Handles:
                    return base
        except:
            pass


    def register_all(self, module):
        for _, type in inspect.getmembers(module, predicate=inspect.isclass):
            self.register(type)

    def register(self, type):
        handler_service_type = self.get_message_type(type)
        if handler_service_type is None:
            return
        container.register(handler_service_type, type)

    def get_handlers(self, type):
        return self.container.resolve_all(services.Handles[type])


container = punq.Container()

db = orm.SqlAlchemy('sqlite://')
db.recreate_schema()
db.register_in(container)

container.register(ports.IssueViewBuilder, views.IssueViewBuilder)
container.register(ports.IssueListViewBuilder, views.IssueListBuilder)
container.register(domain.emails.EmailSender, adapters.emails.LoggingEmailSender)
messages = PunqMessageRegistry(container)
container.register(ports.HandlerRegistry, messages)
container.register(ports.MessageBus)
messages.register_all(services)
