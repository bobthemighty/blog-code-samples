import collections
import uuid
from .orm import SessionFactory
from issues.domain import ports

# This little helper function converts the binary data
# We store in Sqlite back to a uuid.
# Ordinarily I use postgres, which has a native UniqueID
# type, so this manual unmarshalling isn't necessary


def read_uuid(record, column):
    record = dict(record)
    bytes_val = record[column]
    uuid_val = uuid.UUID(bytes=bytes_val)
    record[column] = uuid_val
    return record


class IssueViewBuilder(ports.IssueViewBuilder):

    _q = """SELECT description,
                 reporter_email,
                 reporter_name
            FROM issues
            WHERE issue_id = :id"""

    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    def fetch(self, id):
        session = self.session_factory()
        result = session.execute(self._q, {'id': id.bytes})
        record = result.fetchone()
        return dict(record)


class IssueListBuilder:

    _q = """SELECT issue_id,
                 description,
                 reporter_email,
                 reporter_name
            FROM issues"""

    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    def fetch(self):
        session = self.session_factory()
        query = session.execute(
            'SELECT issue_id, description, reporter_email, reporter_name ' +
            ' FROM issues')

        result = []
        for r in query.fetchall():
            r = read_uuid(r, 'issue_id')
            result.append(r)

        return result
