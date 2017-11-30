from issues.domain.model import Issue, IssueReporter

def handle_report_issue(uow, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with uow:
        uow.issues.add(issue)
        uow.commit()
