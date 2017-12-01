import uuid
from flask import Flask, request, jsonify
from . import config
from issues.adapters.views import view_issue, list_issues


app = Flask('issues')
bus = config.bus


@app.before_request
def get_auth_header():
    request.user = request.headers.get('X-email')

@app.route('/issues', methods=['POST'])
def report_issue():
    issue_id = uuid.uuid4()
    cmd = ReportIssueCommand(issue_id=issue_id, **request.get_json())
    bus.handle(cmd)
    return "", 201, {"Location": "/issues/" + str(issue_id) }

@app.route('/issues/<issue_id>')
def get_issue(issue_id):
    view = view_issue(db.config.get_session(), uuid.UUID(issue_id))
    return jsonify(view)

@app.route('/issues', methods=['GET'])
def list_issues():
    view = list_issues(db.config.get_session())
    return jsonify(view)

@app.route('/issues/<issue_id>/assign', methods=['POST'])
def assign_to_engineer(issue_id):
    assign_to = request.args.get('engineer')
    cmd = AssignIssueCommand(issue_id, assign_to, request.user)
    bus.handle(cmd)
    return "", 200

@app.route('/issues/<issue_id>/pick', methods=['POST'])
def pick_issue(issue_id):
    cmd = PickIssueCommand(issue_id, request.user)
    bus.handle(cmd)
    return
