from typing import NamedTuple

class ReportIssueCommand(NamedTuple):

    reporter_name: str
    reporter_email: str
    problem_description: str
