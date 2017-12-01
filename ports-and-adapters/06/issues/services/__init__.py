import issues.domain.emails
from issues.domain.model import Issue, IssueReporter
from issues.domain import emails, messages


def report_issue (start_uow, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with start_uow() as tx:
        tx.issues.add(issue)
        tx.commit()

def triage_issue (start_uow, cmd):
    with start_uow() as tx:
        issue = tx.issues.get(cmd.issue_id)
        issue.triage(cmd.priority, cmd.category)
        tx.commit()

def pick_issue (start_uow, cmd):
    with start_uow() as tx:
        issue = tx.issues.get(cmd.issue_id)
        issue.assign(cmd.picked_by)
        tx.commit()

def assign_issue (start_uow, cmd):
    with start_uow() as tx:
        issue = tx.issues.get(cmd.issue_id)
        issue.assign(cmd.assigned_to, cmd.assigned_by)
        tx.commit()

def on_issue_assigned_to_engineer(view_issue, sender, evt):
    data = view_issue(evt.issue_id)
    data.update(**evt._asdict())

    request = emails.MailRequest(
        emails.IssueAssignedToMe,
        emails.default_from_addr,
        emails.EmailAddress(evt.assigned_to),
        )

    sender.send(request, data)


