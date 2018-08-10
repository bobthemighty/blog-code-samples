import collections
import logging
import typing
import uuid

import sqlalchemy
from sqlalchemy.pool import StaticPool
from sqlalchemy import (Table, Column, MetaData, String, Integer, Text,
                        ForeignKey, create_engine, event)
from sqlalchemy.orm import mapper, scoped_session, sessionmaker, composite, relationship
import sqlalchemy.exc
import sqlalchemy.orm.exc

from sqlalchemy_utils.functions import create_database, drop_database
from sqlalchemy_utils.types.uuid import UUIDType

from issues.domain.model import Issue, IssueReporter, Assignment
from issues.domain.ports import (IssueLog, UnitOfWork, UnitOfWorkManager,
                                 MessageBus)

SessionFactory = typing.Callable[[], sqlalchemy.orm.Session]


class IssueRepository(IssueLog):

    def __init__(self, session):
        self._session = session

    def add(self, issue: Issue) -> None:
        self._session.add(issue)

    def _get(self, issue_id) -> Issue:
        return self._session.query(Issue).\
            filter_by(id=issue_id).\
            first()


class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, sessionfactory: SessionFactory, bus: MessageBus) -> None:
        self.sessionfactory = sessionfactory
        self.bus = bus
        event.listen(self.sessionfactory, "after_flush", self.gather_events)
        event.listen(self.sessionfactory, "loaded_as_persistent",
                     self.setup_events)

    def __enter__(self):
        self.session = self.sessionfactory()
        self.flushed_events = []
        return self

    def __exit__(self, type, value, traceback):
        self.publish_events()

    def commit(self):
        self.session.flush()
        self.session.commit()

    def rollback(self):
        self.flushed_events = []
        self.session.rollback()

    def setup_events(self, session, entity):
        entity.events = []

    def gather_events(self, session, ctx):
        flushed_objects = [e for e in session.new] + [e for e in session.dirty]
        for e in flushed_objects:
            try:
                self.flushed_events += e.events
            except AttributeError:
                pass

    def publish_events(self):
        for e in self.flushed_events:
            self.bus.handle(e)

    @property
    def issues(self):
        return IssueRepository(self.session)


class SqlAlchemy:

    def __init__(self, uri, bus):
        # re: connect_args and StaticPool, see
        # http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
        self.engine = create_engine(
            uri,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        self.bus = bus
        self._session_maker = scoped_session(sessionmaker(self.engine),)

    def recreate_schema(self):
        self.configure_mappings()
        drop_database(self.engine.url)
        self.create_schema()

    def get_session(self):
        return self._session_maker()

    def start_unit_of_work(self):
        return SqlAlchemyUnitOfWork(self._session_maker, self.bus)

    def create_schema(self):
        create_database(self.engine.url)
        self.metadata.create_all()

    def configure_mappings(self):
        self.metadata = MetaData(self.engine)

        IssueReporter.__composite_values__ = lambda i: (i.name, i.email)
        issues = Table('issues', self.metadata,
                       Column('pk', Integer, primary_key=True),
                       Column('issue_id', UUIDType),
                       Column('reporter_name', String(50)),
                       Column('reporter_email', String(50)),
                       Column('description', Text))

        assignments = Table(
            'assignments',
            self.metadata,
            Column('pk', Integer, primary_key=True),
            Column('id', UUIDType),
            Column('fk_assignment_id', UUIDType, ForeignKey('issues.issue_id')),
            Column('assigned_by', String(50)),
            Column('assigned_to', String(50)),
        )

        mapper(
            Issue,
            issues,
            properties={
                '__pk':
                issues.c.pk,
                'id':
                issues.c.issue_id,
                'description':
                issues.c.description,
                'reporter':
                composite(IssueReporter, issues.c.reporter_name,
                          issues.c.reporter_email),
                '_assignments':
                relationship(Assignment, backref='issue')
            },
        ),

        mapper(
            Assignment,
            assignments,
            properties={
                '__pk': assignments.c.pk,
                'id': assignments.c.id,
                'assigned_to': assignments.c.assigned_to,
                'assigned_by': assignments.c.assigned_by
            })
