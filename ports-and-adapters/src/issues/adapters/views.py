import collections
import uuid
from .orm import SessionFactory
from issues.domain import ports

# This little helper function converts the binary data
# We store in Sqlite back to a uuid.
# Ordinarily I use postgres, which has a native UniqueID
# type, so this manual unmarshalling isn't necessary


def read_uuid(record):
    record = dict(record)
    bytes_val = record['issue_id']
    uuid_val = uuid.UUID(bytes=bytes_val)
    record['issue_id'] = uuid_val
    return record


FETCH_ISSUE = """SELECT
                 issue_id,
                 description,
                 reporter_email,
                 reporter_name
            FROM issues
            WHERE issue_id = :issue_id"""

LIST_ISSUES = """SELECT issue_id,
                 description,
                 reporter_email,
                 reporter_name
            FROM issues"""


def view_issue(make_session, id):
    session = make_session()
    result = session.execute(FETCH_ISSUE, {'issue_id': id.bytes})
    record = result.fetchone()
    return read_uuid(record)


def list_issues(make_session):
    session = make_session()
    query = session.execute(LIST_ISSUES)

    result = []
    for r in query.fetchall():
        result.append(read_uuid(r))

    return result
