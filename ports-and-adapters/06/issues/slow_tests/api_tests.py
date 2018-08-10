import requests
from expects import expect, equal


def report_issue(reporter_name='fred',
                 reporter_email='fred@example.org',
                 problem_description='Halp!!!1!!1!11eleven!'):
    data = {
        'reporter_name': reporter_name,
        'reporter_email': reporter_email,
        'problem_description': problem_description
    }

    resp = requests.post('http://localhost:5000/issues', json=data)
    assert resp.ok, f'Got code {resp.status_code}, response was {resp.text}'
    return resp.headers['Location']


class When_reporting_a_new_issue:

    def because_we_report_a_new_issue(self):
        self.location = report_issue('Arnold', 'arnold@example.org',
                                     "I'm all alone and frightened.")

    @property
    def the_issue(self):
        return requests.get(self.location).json()

    def it_should_have_the_correct_reporter(self):
        expect(self.the_issue['reporter_name']).to(equal('Arnold'))

    def it_should_have_the_correct_description(self):
        expect(self.the_issue['description']).to(
            equal('I\'m all alone and frightened.'))


class When_assigning_an_issue_to_another_engineer:

    def given_an_issue(self):
        self.location = report_issue('Arnold', 'arnold@example.org',
                                     "I'm all alone and frightened")

    def because_barbara_assigns_the_issue_to_constance(self):
        self.response = requests.post(
            self.location + '/assign?engineer=constance',
            headers={
                'X-Email': 'barbara@example.org'
            })

    def it_should_be_fine(self):
        expect(self.response.status_code).to(equal(200))
