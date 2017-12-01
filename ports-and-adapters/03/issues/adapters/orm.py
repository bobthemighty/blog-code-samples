import collections
import logging
import uuid

import sqlalchemy
from sqlalchemy import (
        Table, Column, MetaData, String, Integer, Text,
        create_engine)
from sqlalchemy.orm import mapper, scoped_session, sessionmaker, composite
import sqlalchemy.exc
import sqlalchemy.orm.exc

from sqlalchemy_utils.functions import create_database, drop_database
from sqlalchemy_utils.types.uuid import UUIDType

from issues.domain.model import Issue, IssueReporter
from issues.domain.ports import (
    UnitOfWork,
)




class IssueRepository:

    def __init__(self, session):
        self._session = session

    def add(self, issue: Issue) -> None:
        self._session.add(issue)


class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, start_session):
        self.start_session = start_session

    def __enter__(self):
        self.session = self.start_session()
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @property
    def issues(self):
        return IssueRepository(self.session)


class SqlAlchemy:

    def __init__(self, uri):
        self.engine = create_engine(uri)

    def get_unit_of_work(self):
        return SqlAlchemyUnitOfWork(self.start_session)

    def recreate_schema(self):
        drop_database(self.engine.url)
        self.create_schema()

    def create_schema(self):
        create_database(self.engine.url)
        self.metadata.create_all()

    def start_session(self):
        return scoped_session(sessionmaker(self.engine))

    def configure_mappings(self):
        self.metadata = MetaData(self.engine)

        IssueReporter.__composite_values__ = lambda i: (i.name, i.email)
        issues = Table(
            'issues',
            self.metadata,
            Column('pk', Integer, primary_key=True),
            Column('issue_id', UUIDType),
            Column('reporter_name', String(50)),
            Column('reporter_email', String(50)),
            Column('description', Text)
        )
        mapper(
            Issue,
            issues,
            properties={
                '__pk': issues.c.pk,
                'id': issues.c.issue_id,
                'description': issues.c.description,
                'reporter': composite(IssueReporter,
                    issues.c.reporter_name,
                    issues.c.reporter_email)
            },
        )

