import inspect
import logging

from . import orm

from .emails import LoggingEmailSender

import issues.domain.messages as msg
from issues.domain import ports
from issues import services, domain, adapters
from issues.adapters import views

db = orm.SqlAlchemy('sqlite://')
db.recreate_schema()

bus = ports.MessageBus()
