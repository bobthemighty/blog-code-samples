from functools import partial
import inspect
import logging

from . import orm

from .emails import send_to_stdout

import issues.domain.messages as msg
from issues.domain import ports, emails
from issues import services, domain, adapters
from issues.adapters import views

bus = ports.MessageBus()
db = orm.SqlAlchemy('sqlite://', bus)
db.recreate_schema()


def make_pipeline(handler, *args):
    return services.pipeline(services.logging_handler, services.metric_recorder,
                             partial(handler, *args))


bus.register(msg.ReportIssue,
             make_pipeline(services.report_issue, db.start_unit_of_work))

bus.register(msg.TriageIssue,
             make_pipeline(services.triage_issue, db.start_unit_of_work))

bus.register(msg.PickIssue,
             make_pipeline(services.pick_issue, db.start_unit_of_work))

bus.register(msg.AssignIssue,
             make_pipeline(services.assign_issue, db.start_unit_of_work))

bus.register(msg.IssueAssignedToEngineer,
             make_pipeline(services.on_issue_assigned_to_engineer,
                           partial(views.view_issue, db.get_session),
                           emails.EmailSender(send_to_stdout)))
