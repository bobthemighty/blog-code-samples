from issues.domain.model import Issue, IssueReporter
from issues.domain.ports import UnitOfWorkManager

def handle_report_issue(uowm: UnitOfWorkManager, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with uowm.start() as tx:
        tx.issues.add(issue)
        tx.commit()
