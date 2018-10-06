import uuid
from flask import Flask, request, jsonify
from . import config
from issues.domain.messages import ReportIssue, AssignIssue, PickIssue
from issues.adapters import views

app = Flask('issues')
bus = config.bus
db = config.db


@app.before_request
def get_auth_header():
    request.user = request.headers.get('X-email')


@app.route('/issues', methods=['POST'])
def report_issue():
    issue_id = uuid.uuid4()
    cmd = ReportIssue(issue_id=issue_id, **request.get_json())
    bus.handle(cmd)
    return "", 201, {"Location": "/issues/" + str(issue_id)}


@app.route('/issues/<issue_id>')
def get_issue(issue_id):
    view = views.view_issue(db.get_session, uuid.UUID(issue_id))
    return jsonify(view)


@app.route('/issues', methods=['GET'])
def list_issues():
    view = views.list_issues(db.get_session)
    return jsonify(view)


@app.route('/issues/<issue_id>/assign', methods=['POST'])
def assign_to_engineer(issue_id):
    assign_to = request.args.get('engineer')
    cmd = AssignIssue(issue_id, assign_to, request.user)
    bus.handle(cmd)
    return "", 200


@app.route('/issues/<issue_id>/pick', methods=['POST'])
def pick_issue(issue_id):
    cmd = PickIssue(issue_id, request.user)
    bus.handle(cmd)
    return


if __name__ == '__main__':
    app.run()

