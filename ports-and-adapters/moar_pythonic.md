# Ports and Adapters, Message Bus, Unit of Work: (arguably) more Pythonic implementations

Hi, I'm Harry, Bob's coauthor for this series on architecture.  Now I don't pretend
to being an architect, but I do know a bit about Python.  You know the apocryphal tale
about [bikeshedding](https://en.wikipedia.org/wiki/Law_of_triviality)?  Everyone wants to be able to express an opinion, even if it's only
about the colour of the biksheds?  Well this will be me essentially doing that about 
Bob's code.  Not questioning the architecture.  Just the cosmetics.  But, readability
counts, so here we go!


## "Stop Writing Classes"

Despite the fact that Bob swears blind that he was a functional programmer for years,
I think Bob does occacsionally let the OO habits of the C# world take over, and
he sees classes everywhere, including plenty of places where they just don't help.

Like the man said, [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0),
or [escape from the Kingdom of Nouns](https://steve-yegge.blogspot.com/2006/03/execution-in-kingdom-of-nouns.html), 
or perhaps simply:

> It is not enough to simply stop writing Java.  You must also stop yourself from writing
> Java using Another Language.


Let's see if we can't replace a few classes with some more Pythonic patterns, and see if
it makes some of those architectural patterns easier to read, implement and understand.


# Command handlers as functions


> If a class only has one method other than its constructor, it should probably be a function
 - Jack Diederich


or

> look for classes with names like "Handler", "Maker", "Builder", "Factory", and you'll probably
> find some good candidates for converting to functions
-Me.  but hardly a novel thought.

If you're implementing the _Command Handler_ pattern, you're going to need to represent
commands and handlers.

For commands I can't really fault Bob's use of namedtuples, as imported from
the `typing` module:

```python
class ReportIssueCommand(NamedTuple):
    issue_id: UUID
    reporter_name: str
    reporter_email: str
    problem_description: str
```
This wasn't available at the time of writing, but [Python 3.7 dataclasses]()
might be worth a look too. You'd probably want to use `frozen=True` to
replicate the immutabilty of namedtuples...

But for handlers, use of a class is probably more up for debate:

```python
class ReportIssueHandler(Handles[messages.ReportIssueCommand]):

    def __init__(self, uowm: UnitOfWorkManager):
        self.uowm = uowm

    def handle(self, cmd):
        reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
        issue = Issue(cmd.issue_id, reporter, cmd.problem_description)

        with self.uowm.start() as uow:
            uow.issues.add(issue)
            uow.commit()
```

Even the word "handler" definitely feels like a case of nouning a verb.  How about:

```python
def report_issue(start_uow, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with start_uow() as uow:
        uow.issues.add(issue)
        uow.commit()
```

## credit where credit's due?

You need some way of connecting commands with their handlers.  The most boring way of
doing that is in some sort of bootstrap/config code, but you might want to do so 
"inline" in your handler definition.

Bob's way, where the handler class inherits from
`Handles[message.ReportIssueCommand]` definitely deserves some points for being
easily readable, although you might not want to get into the sausage-factory
of the actual implementation, involving, as it does, the controversial `typing` module.


Instead, a decorator might do the trick:

```python
@handles(messages.ReportIssueCommand)
def report_issue(start_uow, cmd):
    ...
```


Of course that might interfere with your (possible) desire to use decorators for dependency injection:


```python
@inject('start_uow')
def report_issue(start_uow, cmd):
    ...
```



# managing units of work without a UnitOfWorkManager


The **Unit of Work** pattern is one of the more straightforward ones; it's easy to understand
why you might want to manage blocks of code that need to be executed "together"
and atomically.

In a simple project that might just mean wrapping everything in a single
database transaction, but you might also want to manage some other types of
permanent storage (filesystem, cloud storage...).

If you're using domain events, you might also want to apply the unit-of-work concept
to them as well:  for a given block of code, perhaps a command handler, either raise
all the events in the happy case, or raise none at all (analogous to a rollback) if an error
occurs at any point. This gives you the option to replay the command handler later without
worrying about duplicate events.

In that case your unit of work manager needs to grow some logic for tracking a stack of events
raised by a block of code, as suggested in the [domain events post](https://io.made.com/why-use-domain-events/).

Either way, a Python context manager is the right pattern here, but does the
implementation really need to involve three different classes?

```python
class SqlAlchemy:

    def __init__(self, uri):
        self.engine = create_engine(uri)
        self._session_maker = scoped_session(sessionmaker(self.engine),)

    @property
    def unit_of_work_manager(self):
        return SqlAlchemyUnitOfWorkManager(self._session_maker, self.bus)


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self, session_factory: SessionFactory, bus: MessageBus):
        self.session_factory = session_factory
        self.bus = bus

    def start(self):
        return SqlAlchemyUnitOfWork(self.session_factory, self.bus)


class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session_factory, bus):
        ...

    def __enter__(self):
        ...

    def __exit__(self):
        ...

    def commit(self):
        ...

    def gather_events(self, session, ctx):
        ...
```


Each class does have a purpose of course:

* `SqlAlchemy` captures config info about SqlAlchemy and our database engine, it has methods like `create_schema` that can re-create
  the database for us if we need.
* `SqlAlchemyUnitOfWorkManager` is meant to hold logic about when to create new database sessions and when to re-use existing ones
* `SqlAlchemyUnitOfWork` is the actual context manager that holds the logic for commits, rollbacks, and publishing events atomically.

But can we make things a little simpler?  SqlAlchemy itself already manages sessions for us.  Perhaps we could just have one
model for the database, and another for the units of work?


```python
from sqlalchemy.orm import sessionmaker

class SqlAlchemy:

    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.session_factory = sessionmaker(self.engine)

    def start_unit_of_work(self):
        return SqlAlchemyUnitOfWork(self.session_factory, self.bus)
```


If you're not using domain events and your unit of work is simple enough,
perhaps just a database transaction, that you can get away with a single
method, using `contextlib.contextmanager` and the `yield` keyword:

```python
from contextlib import contextmanager

class SqlAlchemy:
    ...

    @contextmanager
    def start_unit_of_work(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
```
Although if the only thing you're putting into your unit of work is a database transaction, perhaps
you don't need a unit-of-work class at all?

