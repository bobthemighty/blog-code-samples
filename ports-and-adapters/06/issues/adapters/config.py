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

bus.register(msg.ReportIssue, services.report_issue, db.start_unit_of_work)

bus.register(msg.TriageIssue, services.triage_issue, db.start_unit_of_work)

bus.register(msg.PickIssue, services.pick_issue, db.start_unit_of_work)

bus.register(msg.IssueAssignedToEngineer,
             services.on_issue_assigned_to_engineer,
             partial(views.view_issue, db.get_session),
             emails.EmailSender(send_to_stdout))
