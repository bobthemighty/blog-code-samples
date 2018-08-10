# Ports and Adapters, Message Bus, Unit of Work: (arguably) more Pythonic implementations

Hi, I'm Harry, Bob's coauthor for this series on architecture.  I know next to nothing
about architecture, but I do know a bit about Python, enough to recognise that,
despite his assurances that he was a functional progammer for years, he's let
the OO habits of the C# world take over, and he sees classes everywhere, including
plenty of places where they just don't help.

Like the man said, [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0),
or [escape from the Kingdom of Nouns](https://steve-yegge.blogspot.com/2006/03/execution-in-kingdom-of-nouns.html), 
or perhaps simply:

> It is not enough to simply stop writing Java.  You must also stop yourself from writing
> Java using Another Language.


# Events and Command handlers as functions

> If a class only has one method other than its constructor, it should probably be a function


or

> look for classes with names like "Handler", "Maker", "Builder", "Factory", and you'll probably
> find some good candidates for converting to functions

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

# vs

def report_issue(start_uow, cmd):
    reporter = IssueReporter(cmd.reporter_name, cmd.reporter_email)
    issue = Issue(cmd.issue_id, reporter, cmd.problem_description)
    with start_uow() as uow:
        uow.issues.add(issue)
        uow.commit()

# or, if you're using some sort of DI tool

@inject('start_uow')
def report_issue(cmd):
    ...
```


# managing units of work without a UnitOfWorkManager


```python

class SqlAlchemy:

    def __init__(self, uri):
        self.engine = create_engine(uri)
        self._session_maker = scoped_session(sessionmaker(self.engine),)

    @property
    def unit_of_work_manager(self):
        return SqlAlchemyUnitOfWorkManager(self._session_maker, self.bus)


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):

    def __init__(self, session_maker: SessionFactory, bus: MessageBus):
        self.session_maker = session_maker
        self.bus = bus

    def start(self):
        return SqlAlchemyUnitOfWork(self.session_maker, self.bus)

# vs


class SqlAlchemy:

    def __init__(self, uri):
        ...

    def start_unit_of_work(self):
        return SqlAlchemyUnitOfWork(self._session_maker, self.bus)

# or even



```
