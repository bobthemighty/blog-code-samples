from issues.domain.ports import IssueLog, UnitOfWork


class FakeIssueLog(IssueLog):

    def __init__(self):
        self.issues = []

    def add(self, issue):
        self.issues.append(issue)

    def get(self, id):
        return self.issues[id]

    def __len__(self):
        return len(self.issues)

    def __getitem__(self, idx):
        return self.issues[idx]


class FakeUnitOfWork(UnitOfWork):

    def __init__(self):
        self._issues = FakeIssueLog()

    def start(self):
        self.was_committed = False
        self.was_rolled_back = False
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.exn_type = type
        self.exn = value
        self.traceback = traceback

    def commit(self):
        self.was_committed = True

    def rollback(self):
        self.was_rolled_back = True

    @property
    def issues(self):
        return self._issues
