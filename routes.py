import json
from db import db, Group, Event
from flask import Flask, request

db_filename = "hackapp.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
  db.create_all()

@app.route('/api/groups/')
def get_groups():
  """Return all currently stored groups."""
  groups = Group.query.all()
  res = {'success': True, 'data': [group.serialize() for group in groups]}
  return json.dumps(res), 200

@app.route('/api/groups/', methods=['POST'])
def create_group():
  """Create new group specified by the user's input."""
  group_body = json.loads(request.data)
  if 'title' not in group_body or 'username' not in group_body:
    return json.dumps({'success': False, 'error': 'Needs title or username'}), 404
  group = Group(
      title=post_body.get('text'),
      admin=post_body.get('username'),
      info=post_body.get('info')
  )
  db.session.add(group)
  db.session.commit()
  return json.dumps({'success': True, 'data': group.serialize()}), 201


@app.route('/api/group/<int:group_id>/')
def get_group(group_id):
  """Return the group specified by the groups id."""
  group = Group.query.filter_by(id=group_id).first()
  if group is not None:
    return json.dumps({'success': True, 'data': group.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Group not found!'}), 404


