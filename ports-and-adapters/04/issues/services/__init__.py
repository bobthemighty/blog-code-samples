import issues.domain.emails
from issues.domain.model import Issue, IssueReporter
from issues.domain.ports import UnitOfWorkManager, IssueViewBuilder
from issues.domain import emails


class ReportIssueHandler:

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
        issue = Issue(cmd.issue_id, reporter, cmd.problem_description)

        with self.uowm.start() as tx:
            tx.issues.add(issue)
            tx.commit()


class TriageIssueHandler:

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        with self.uowm.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.triage(cmd.priority, cmd.category)
            tx.commit()


class PickIssueHandler:

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        with self.uowm.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.assign(cmd.picked_by)
            tx.commit()


class AssignIssueHandler:

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        with self.uowm.start() as tx:
            issue = tx.issues.get(cmd.issue_id)
            issue.assign(cmd.assigned_to, cmd.assigned_by)
            tx.commit()


class IssueAssignedHandler:

    def __init__(self, view_builder: IssueViewBuilder,
                 sender: emails.EmailSender):
        self.sender = sender
        self.view_builder = view_builder

    def handle(self, evt):
        data = self.view_builder.fetch(evt.issue_id)
        data.update(**evt._asdict())
        request = emails.MailRequest(
            emails.IssueAssignedToMe,
            emails.default_from_addr,
            emails.EmailAddress(evt.assigned_to),
        )

        self.sender.send(request, data)
