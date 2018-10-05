from issues.domain.model import Issue, IssueReporter
from issues.domain import emails


def report_issue(start_uow, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with start_uow() as uow:
        uow.issues.add(issue)
        uow.commit()


def triage_issue(start_uow, cmd):
    with start_uow() as uow:
        issue = uow.issues.get(cmd.issue_id)
        issue.triage(cmd.priority, cmd.category)
        uow.commit()


def pick_issue(start_uow, cmd):
    with start_uow() as uow:
        issue = uow.issues.get(cmd.issue_id)
        issue.assign(cmd.picked_by)
        uow.commit()


def assign_issue(start_uow, cmd):
    with start_uow() as uow:
        issue = uow.issues.get(cmd.issue_id)
        issue.assign(cmd.assigned_to, cmd.assigned_by)
        uow.commit()


def on_issue_assigned_to_engineer(view_issue, sender, evt):
    data = view_issue(evt.issue_id)
    data.update(**evt._asdict())

    request = emails.MailRequest(
        emails.IssueAssignedToMe,
        emails.default_from_addr,
        emails.EmailAddress(evt.assigned_to),
    )

    sender.send(request, data)
