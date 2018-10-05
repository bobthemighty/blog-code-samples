from expects.matchers import Matcher


class have_raised(Matcher):

    def __init__(self, event):
        self.event = event

    def _match(self, entity):
        return self.event in entity.events, []
