import uuid
from flask import Flask, request, jsonify
from issues.adapters.orm import SqlAlchemy
from issues.adapters.views import view_issue, IssueListBuilder

from issues.services import handle_report_issue
from issues.domain.commands import ReportIssueCommand

app = Flask('issues')

db = SqlAlchemy('sqlite:///issues.db')
db.configure_mappings()
db.create_schema()



@app.route('/issues', methods=['POST'])
def report_issue():
    issue_id = uuid.uuid4()
    cmd = ReportIssueCommand(issue_id=issue_id, **request.get_json())
    handle_report_issue(db.unit_of_work_manager, cmd)
    return "", 201, {"Location": "/issues/" + str(issue_id)}


@app.route('/issues/<issue_id>')
def get_issue(issue_id):
    session = db.get_session()
    issue_view = view_issue(session, uuid.UUID(issue_id))
    return jsonify(issue_view)


@app.route('/issues', methods=['GET'])
def list_issues():
    session = db.get_session()
    view_builder = IssueListBuilder(session)
    view = view_builder.fetch()
    return jsonify(view)
