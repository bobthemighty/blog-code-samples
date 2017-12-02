from issues.domain.model import Issue, IssueReporter
from issues.domain.ports import UnitOfWorkManager


class ReportIssueHandler:

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
        issue = Issue(reporter, cmd.problem_description)

        with self.uowm.start() as tx:
            tx.issues.add(issue)
            tx.commit()
