from enum import Enum
from uuid import UUID
from typing import NamedTuple

class IssueState(Enum):
    AwaitingTriage = 0
    AwaitingAssignment = 1
    ReadyForWork = 2

class IssuePriority(Enum):
    NotPrioritised = 0
    Low = 1
    Normal = 2
    High = 3
    Urgent = 4



class ReportIssueCommand(NamedTuple):
    issue_id: UUID
    reporter_name: str
    reporter_email: str
    problem_description: str


class TriageIssueCommand(NamedTuple):
    issue_id: UUID
    category: str
    priority: IssuePriority


class AssignIssueCommand(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


class IssueAssignedToEngineer(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


class IssueReassigned(NamedTuple):
    issue_id: UUID
    previous_assignee: str
