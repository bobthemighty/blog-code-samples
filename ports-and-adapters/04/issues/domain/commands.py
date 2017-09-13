from uuid import UUID
from typing import NamedTuple
from .model import Issue

class ReportIssueCommand(NamedTuple):
    issue_id: UUID
    reporter_name: str
    reporter_email: str
    problem_description: str


class TriageIssueCommand(NamedTuple):
    issue_id: UUID
    category: str
    priority: Issue.Priority
