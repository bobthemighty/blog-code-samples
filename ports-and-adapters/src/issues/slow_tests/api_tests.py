import time
import sys
from pathlib import Path
import requests
import subprocess
from expects import expect, equal

class GivenAnAPIServer:
    def given_an_api_server(self):
        cwd = Path(__file__).parent / '../..'
        self.server = subprocess.Popen([
            sys.executable, '-m', 'issues.adapters.flask'
        ], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._wait_for_server_to_start()

    def _wait_for_server_to_start(self):
        start = time.time()
        while time.time() < start + 3:
            try:
                requests.get('http://localhost:5000')
                return
            except Exception as e:
                print(e, type(e))
                time.sleep(0.2)
        stdout, stderr = '', ''
        rc = self.server.poll()
        if rc:
            stdout, stderr = self.server.stdout.read(), self.server.stderr.read()
        raise Exception(
            f'server did not start, return code was {rc}.\n'
            f'stdout:\n{stdout}\n\nstderr:\n{stderr}\n'
        )

    def cleanup_server(self):
        self.server.kill()


def report_issue(reporter_name='fred',
                 reporter_email='fred@example.org',
                 problem_description='Halp!!!1!!1!11eleven!'):
    data = {
        'reporter_name': reporter_name,
        'reporter_email': reporter_email,
        'problem_description': problem_description
    }

    resp = requests.post('http://localhost:5000/issues', json=data)
    return resp.headers['Location']


class When_reporting_a_new_issue(GivenAnAPIServer):

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


class When_assigning_an_issue_to_another_engineer(GivenAnAPIServer):

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
