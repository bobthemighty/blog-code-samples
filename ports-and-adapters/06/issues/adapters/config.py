from functools import partial
import inspect
import logging

from . import orm

from .emails import LoggingEmailSender

import issues.domain.messages as msg
from issues.domain import ports
from issues import services, domain, adapters
from issues.adapters import views

bus = ports.MessageBus()
db = orm.SqlAlchemy('sqlite://', bus)
db.recreate_schema()


bus.register(msg.ReportIssue, partial(
    services.report_issue,
    db.start_unit_of_work
))

bus.register(msg.TriageIssue, partial(
    services.triage_issue,
    db.start_unit_of_work
))

bus.register(msg.PickIssue, partial(
    services.pick_issue,
    db.start_unit_of_work
))

bus.register(msg.IssueAssignedToEngineer, partial(
    services.on_issue_assigned_to_engineer,
    partial(views.view_issue, db.get_session)
))
