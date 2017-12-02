from enum import Enum
from uuid import UUID
from typing import NamedTuple


def event(cls):

    setattr(cls, 'is_cmd', property(lambda x: getattr(x, 'is_cmd', False)))
    setattr(cls, 'is_event', property(lambda x: getattr(x, 'is_event', True)))
    setattr(cls, 'id', property(lambda x: getattr(x, 'id', None)))

    return cls


def command(cls):

    setattr(cls, 'is_cmd', property(lambda x: getattr(x, 'is_cmd', True)))
    setattr(cls, 'is_event', property(lambda x: getattr(x, 'is_event', False)))
    setattr(cls, 'id', property(lambda x: getattr(x, 'id', None)))

    return cls


class Message(NamedTuple):
    id: UUID


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


@command
class ReportIssueCommand(NamedTuple):
    issue_id: UUID
    reporter_name: str
    reporter_email: str
    problem_description: str


@command
class TriageIssueCommand(NamedTuple):
    issue_id: UUID
    category: str
    priority: IssuePriority


@command
class AssignIssueCommand(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


@command
class PickIssueCommand(NamedTuple):
    issue_id: UUID
    picked_by: str


@event
class IssueAssignedToEngineer(NamedTuple):
    issue_id: UUID
    assigned_to: str
    assigned_by: str


@event
class IssueReassigned(NamedTuple):
    issue_id: UUID
    previous_assignee: str
