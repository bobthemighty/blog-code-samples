Dependency injection is not crazy, not un-pythonic, and not enterprisey. Here's Wikipedia:

> In software engineering, dependency injection is a technique whereby one object (or static method) supplies the dependencies of another object. A dependency is an object that can be used (a service). An injection is the passing of a dependency to a dependent object (a client) that would use it. The service is made part of the client's state. Passing the service to the client, rather than allowing a client to build or find the service, is the fundamental requirement of the pattern

In other words, Dependency Injection (DI, for all you jargon-fans out there) is when an object is given its dependencies instead of reaching out to get them by itself. For example, in this series we're building a system for managing IT support issues. Last time we had a requirement to send an email when an issue was assigned to an engineer.


## Dependency injection in class constructors

Our handler is orchestration code, and it plugs together two collaborators: a View Builder that fetches data, and an Email Sender that knows how to send an email to the mail server.

We could have our handler import and use its dependencies directly (and implicitly), like this:

```python
from views import IssueViewBuilder
from email_sender import EmailSender
from orm import db

class IssueAssignedHandler:

    def handle(self, cmd):
        issue_data = IssueViewBuilder(db).fetch(cmd.issue_id)
        EmailSender().send_email(emails.IssueAssigned, issue_data)

```
Instead, we make the handler ask for the Email Sender and the View Builder in its constructor:

```python
class IssueAssignedHandler:

    def __init__(self, sender: EmailSender, view: IssueViewBuilder):
        self.sender = sender
        self.view = view

    def handle(self, cmd):
        data = self.view.fetch(cmd.issue_id)
        sender.send_email(emails.IssueAssigned, data)
```

This is dependency injection. We're going to be injecting the dependencies (the sender and view) by making them parameters of the constructor. That's it.

Why bother?  Passing our parameters this way makes them more explicit, and so reduces the overall quantity of Unpleasant Surprise hiding in the system.  It's easy to see what might have side-effects and what doesn't. Because I'm providing all my dependencies from outside of my handler, I can change them easily, or provide fakes for testing. This helps to keep the system loosely-coupled and flexible. It also means that I have to think about what the dependencies of my system *ought to be*, and that helps me to define meaningful abstractions.



## Dependency injection with partial functions


In our implementation, dependency injection is really just a way of performing partial application on a method call. Earlier in this series, I said that I often create handlers by abusing the `__call__` magic method.

```python
class IssueAssignedHandler:

    def __init__(self, sender, view):
        self.view = view
        self.sender = sender

    def __call__(self, cmd):
        data = self.view.fetch(cmd.issue_id)
        sender.send_email(emails.IssueAssigned, data)

handler = IssueAssignedHandler(sender, view)
handler(cmd)
```

Here, calling the constructor of IssueAssignedHandler returns a callable. Compare that with the following examples of partial application:

```python
def explicit_closure_handler(self, sender, view):

    def h(self, cmd):
        data = view.fetch(cmd.issue_id)
        ...
    return h

handler_a = explicit_closure_handler(sender, view)
handler_a(cmd)

# or:

from functools import partial

def send_assignment_email(sender, view, cmd):
    data = view.fetch(cmd.issue_id)
    ...

handler_b = partial(send_assignment_email, sender, view)
handler_b(cmd)
```

The callables `handler`, `handler_a`, and `handler_b` all take a single argument (the command) and run the same code on it, so we can see that they are equivalent. Dependency injection is just a way of parametising the behaviour of our applications by partially applying function arguments.


## Dependency Injection enables Clean Architecture

The advantage of building a system this way is that it's very easy to test, configure, and extend the behaviour of our application through composition. Dynamic languages offer many ways to fake the behaviour of a component, but my preference is to write explicit fakes and stubs (not just `unittest.mock.Mock` objects), and pass them as constructor arguments. This forces me to think about my system in terms of composable parts, and to identify the roles that they play. Instead of directly calling the database from my handler, I'm providing an `IssueViewBuilder`. Instead of writing a load of SMTP code in my handler, I'm providing an instance of `EmailSender`.

This, for me at least, is the simplest, most obvious, and least magical way of dealing with dependencies, especially across architectural boundaries. Performing dependency injection - whether by constructor injection or partial application, or some magic property-filling decorator - is mandatory if you want to do ports and adapters. It's the "one weird trick" that allows high-level code (business logic) to remain completely isolated from low level code (database transactions, file operations, email sending etc.)


# You don't need to use a framework for DI

Dependency injection gets a bad rap in the Python community for reasons that escape me. But I think one of them is that people assume that you need to use a framework to perform the injection, and they're terrified of ending up in an xml-driven hellscape like Spring. This isn't true, you can still perform dependency injection with no frameworks at all. For example, in the code sample for the previous part in this series, I extracted all my wiring into a single module with boring code that looks like this:

```python
db = SqlAlchemy('sqlite:///issues.db')
db.configure_mappings()
db.create_schema()

bus = MessageBus()
db.associate_message_bus(bus)

issue_view_builder = IssueViewBuilder(db)
issue_list_builder = IssueListBuilder(db)

report_issue = ReportIssueHandler(db.unit_of_work_manager)
assign_issue = AssignIssueHandler(db.unit_of_work_manager)
triage_issue = TriageIssueHandler(db.unit_of_work_manager)
issue_assigned = IssueAssignedHandler(issue_view_builder, LoggingEmailSender())
bus.subscribe_to(msg.ReportIssueCommand, report_issue)
bus.subscribe_to(msg.TriageIssueCommand, triage_issue)
bus.subscribe_to(msg.IssueAssignedToEngineer, issue_assigned)
bus.subscribe_to(msg.AssignIssueCommand, assign_issue)
```

This code is just a straight-line script that configures the database, creates all of our message handlers, and then registers them with the message bus. This component is what an architect would call a [Composition Root](https://stackoverflow.com/questions/6277771/what-is-a-composition-root-in-the-context-of-dependency-injection). On my current teams, we tend to call this a bootstrap script. As systems grow, though, and requirements become more complex, this bootstrapper script can become more repetitive and error-prone. Dependency injection frameworks exist to remove some of the boiler-plate around registering and wiring up dependencies. In recent years the .Net-hipster crowd have started to move away from complex dependency injection containers in favour of simpler composition roots. This is known as poor man's DI, pure DI, or artisanal organic acorn-fed DI.


# inject


> Dependency injection frameworks exist to remove some of the boiler-plate around registering and wiring up dependencies

Usually, on our Python projects at Made.com, we use the [inject](https://pypi.org/project/Inject/) library. This is a simple tool that performs the partial application trick I demonstrated above. Inject is my favourite of the Python DI libraries because it's so simple to use, but I have a dislike for its use of decorators to declare dependencies.

```python
import inject

# client code

class IssueAssignedHandler:

    @inject(sender='email_sender', view='issue_view_builder')
    def __init__(self, sender, view):
        pass

    def handle(self, cmd):
        pass

# configuration

def configure_binder(binder):
    db = SqlAlchemy('sqlite://')
    binder.bind('email_sender', SmtpEmailSender(host=..., port=..., username=...))
    binder.bind('issue_view_builder', IssueViewBuilder)

inject.configure(configure_binder)

handler = IssueAssignedHandler()
```

The `configure_binder` function takes the place of my bootstrap script in wiring up and configuring my dependencies. When I call `IssueAssignedHandler` the inject library knows that it should replace the `sender` param with the configured SmtpEmailSender, and that it should replace the `view` param with an IssueViewBuilder. The decorator serves to associate the service ("email_sender") with the parameter ("sender"). It works, but it always felt inappropriate to have this kind of declaration outside of my composition root.

# Introducing punq, and DI containers

I've been working on a prototype DI framework that avoids this problem by using Python 3.6's [optional type hinting](https://www.reddit.com/r/Python/comments/5nb0si/why_optional_type_hinting_in_python_is_not_that/), and I'd like to show you some use cases.


```python
import punq

# client code

class IssueAssignedHandler:
    # Instead of a decorator and arbitrary string names, We use
    # type hints of actual classes to declare what dependencies we need
    def __init__(self, sender: EmailSender, view: IssueViewBuilder):
        self.sender = sender
        self.view = view

    def handle(self, cmd):
        pass


# configuration:

container = punq.container()

# We can register a service class
container.register(IssueViewBuilder)

# Or a subclass that implements a service in a particular way
container.register(UnitOfWorkManager, SqlAlchemyUnitOfWorkManager)

# Or a singleton instance of a dependency
container.register(EmailSender, SmtpEmailSender(host=..., port=..))

handler = container.resolve(IssueAssignedHandler)
```

(A ["container"](https://www.martinfowler.com/articles/injection.html) is the established name for a dependency injection framework's registry of services.)


So far, so underwhelming. Simple registrations don't really save us anything over the bootstrap script from earlier. Using a container for this kind of work really only cuts down on duplication - when I've registered UnitOfWorkManager once, I never have to refer to it again, whereas in the bootstrap I had to explicitly pass it to every handler. It's nice not having to decorate my class with dependency injection specific noise though, instead I can just declare what my dependencies are. As an added bonus, I can run `mypy` over my code and it will tell me if I've made any stupid type errors.


# Using DI to compose chains of services

There are more useful things we can do with a dependency injection container, though. For example, maybe we're writing a program that needs to run a bunch of processing rules over some text. We decide to treat each processing rule as a function and use our container to fetch them all at runtime.

```python

# string_processing_rule is just an alias for a function of str -> str
string_processing_rule = Callable[[str], str]

class StringProcessor:

    def __init__(self, rules: List[string_processing_rule]):
        self.rules = rules

    def process(self, input):
        for rules in self.rules:
            input = rule(input)
        return input



def upper_case(input: str) -> str:
    return str.upper()

def reverse(input: str) -> str:
    return reversed(str)


container = punq.container()
container.register(string_processing_rule, upper_case)
container.register(string_processing_rule, reverse)

# `container.resolve` recognises that `StringProcessor` depends on a list of `string_processing_rule` implementations,
# so it makes a list of all the ones it knows about and injects them into the new instance it creates.
processor = container.resolve(StringProcessor)

# prints ("DLORW OLLEH")
print(processor.process("hello world"))
```

One of the advantages of using types over using other keys is that they're composable. I can ask for a List[T] and get all registered instances of some T. This is handy when you're writing code that processes the same message with a bunch on different steps, including rules engines and message buses (see bonus section). Having generics in our type system can make it easier to manage all of our dependencies in other ways, too. For example, I can use generics to automatically wire up all my message handlers.

```python
class IssueAssignedHandler (Handles[IssueAssignedEvent]):
    pass
```

Here we're stating that our `IssueAssignedHandler` is an subtype of the `Handles` class, and it has a type parameter for the handled event. Given a module full of these, I can enumerate the module's types and perform automatic registration.

```python
def register_all(module):
    """ Read through all the types in a module and register them if they are handlers"""
    for _, type in inspect.getmembers(module, predicate=inspect.isclass):
        register(type)

def register(type):
    """ If this type is a handler type then register it in the container """
    handler_service_type = get_message_type(type)
    if handler_service_type is None:
        return
    container.register(handler_service_type, type)

def get_message_type(type):
    """ If this type subclasses the Handles[Msg] class, return the parameterised type.
        eg. for our IssueAssignedHandler, this would return Handles[IssueAssignedEvent]
    """
    try:
        return next(b for b in type.__orig_bases__ if b.__origin__ == services.Handles)
    except (AttributeError, StopIteration):
        return None


def get_handler_for(event_type):
    container.resolve(Handles[event_type])
```


# Nested services

Punq has one more useful trick up its sleeve: nested registrations. These are useful when you need to build some kind of chain of responsibility - a pattern where objects try to handle a request, then pass it along the chain to the next in line.

```python

class MessageHandler:
    def handle(self, msg):
        pass

class LoggingHandler:

    def __init__(self, next: MessageHandler):
        self.next = next

    def handle(self, msg):
        logging.info("Handling message %s", msg)
        try:
            self.next.handle(msg)
            logging.info("Handled message %s", msg)
        except Exception as e:
            logging.exception("Failed to handle message %s", msg)
            raise
```

If punq has multiple services registered for a particular class it will pop one off its stack each time it's asked for one. Because each MessageHandler depends on another MessageHandler, punq treats them as a chain, and injects them into each other like a stack of Russian dolls.

In the following code we add two new message handlers, a metrics handler that records the runtime of our handler pipeline so we can monitor our application, and a de-duplicating handler that prevents us from handling the same message twice. Both of these require complex dependencies of their own, and we can delegate their creation to the container.

```python
class MetricsGatheringHandler(MessageHandler):

    def __init__(self, metrics: MetricsCollector, next: MessageHandler):
        self.metrics = metrics

    def handle(self, msg):
        # Record the time taken when we process a message
        with self.metrics.time('command/execution-time'):
            self.next.handle(msg)


class DeduplicatingHandler(MessageHandler):

    def __init__(self, store:MessageStore, next:MessageHandler):
        self.next = next
        self.store = store

    def handle(self, msg):
        if self.store.contains(msg)
            logging.warn("msg %s is a duplicate. Skipping", msg)
            return

        try:
            self.next.handle(msg)
        finally:
            self.store.add(msg)


container.register(MessageHandler)
container.register(MessageHandler, LoggingHandler)
container.register(MessageHandler, MetricsGatheringHandler)
container.register(MessageHandler, DeduplicatingHandler)
container.register(MetricsCollector, StatsdMetricsCollector)
container.register(MessageFilter, InMemoryMessageFilter)

# Deduplicates, records metrics and writes a log file:
container.resolve(MessageHandler).handle(msg)
```

This is what I meant in the last part when I said that a message bus is a great place to put cross-cutting concerns. By using this pattern of composing generic `MessageHandler` services, we can implement things like validation, logging, exception handling, event database session management.  DI makes it easy for us to write and test those components separately.

# For bonus points: a generic handler can become a message bus implementation

One of the fun side-effects of having a DI container that supports nesting is that we could implement a top-level "God" handler for the generic case whose job is to resolve down to the specific message type, and that effectively becomes the implementation of our message bus:

```python
class DefaultHandler:

    def __init__(self, container:punq.Container):
        self.container = container

    def handle(self, msg):
        handler = container.resolve(Handles[type(msg)])
        handler.handle(msg)

container.register(MessageHandler, DefaultHandler)
container.register(MessageHandler, LoggingHandler)
...
container.register(Handles[IssueAssigned], IssueAssignedHandler)

# Deduplicates, records metrics, etc, 
# and then the DefaultHandler finds and runs the specific handler for this particular msg type,
# egif msg is IssueAssigned, will run IssueAssignedHandler
container.resolve(MessageHandler).handle(msg)
```


Now that I've spent 5 parts building classes, I want to start throwing them all away again and in parts 6 and 7 we'll look at alternative ways of expressing the same architectural patterns.

