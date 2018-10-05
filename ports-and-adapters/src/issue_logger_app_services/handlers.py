from issue_logger_model.domain import Issue, IssueReporter


class ReportIssueHandler:

    def __init__(self, issue_log):
        self.issue_log = issue_log

    def __call__(self, cmd):
        issue = Issue(
            IssueReporter(cmd.reporter_name, cmd.reporter_email),
            cmd.problem_description)
        self.issue_log.add(issue)
