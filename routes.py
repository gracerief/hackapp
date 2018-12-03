import json
from db import db, Group, Event, User
from flask import Flask, request
import users_dao, groups_dao, events_dao

db_filename = "swarm.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
  db.create_all()

#######################################
# AUTH ROUTES

def extract_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return False, json.dumps({'error': 'Missing authorization header.'})

    # Header looks like "Authorization: Bearer <session token>"
    bearer_token = auth_header.replace('Bearer ', '').strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps({'error': 'Invalid authorization header.'})

    return True, bearer_token
    
@app.route('/')
def hello_world():
    return json.dumps({'message': 'Hello, World!'})

@app.route('/register/', methods=['POST'])
def register_account():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    created, user = users_dao.create_user(email, password)

    if not created:
        return json.dumps({'error': 'User already exists.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })

@app.route('/login/', methods=['POST'])
def login():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    success, user = users_dao.verify_credentials(email, password)

    if not success:
        return json.dumps({'error': 'Incorrect email or password.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })

@app.route('/session/', methods=['POST'])
def update_session():
    success, update_token = extract_token(request)

    if not success:
        return update_token

    try:
        user = users_dao.renew_session(update_token)
    except: 
        return json.dumps({'error': 'Invalid update token.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })

@app.route('/secret/', methods=['GET'])
def secret_message():
    success, session_token = extract_token(request)

    if not success:
        return session_token 

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({'error': 'Invalid session token.'})

    return json.dumps({'message': 'You have successfully implemented sessions.'})

@app.route('/users/<int:user_id>/', methods=['POST'])
def update_user(user_id):
  user = User.query.filter_by(id=user_id).first()
  if user is not None:
    post_body = json_loads(request.data)
    user.email = post_body.get('email', user.email)
    user.admin_groups = post_body.get('admin_groups', user.admin_groups)
    user.member_groups = post_body.get('member_groups', user.member_groups)
    user.events = post_body.get('events', user.events)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 200
  return json.dumps({'success': False, 'error': 'User not found!'}), 404


#######################################
# GROUPS ROUTES

@app.route('/api/groups/')
def get_groups():
  """Return all currently stored groups."""
  groups = Group.query.all()
  res = {'success': True, 'data': [group.serialize() for group in groups]}
  return json.dumps(res), 200

@app.route('/api/groups/', methods=['POST'])
def create_group():
  """Create new group specified by the user's input."""
  post_body = json.loads(request.data)
  if 'title' not in post_body or 'username' not in post_body:
    return json.dumps({'success': False, 'error': 'Needs title or admin user'}), 404
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

@app.route('/api/groups/', methods=['POST'])
def create_new_group():
  """Create new group specified by the user's input."""
  post_body = json.loads(request.data)
  if 'title' not in post_body or 'username' not in post_body:
    return json.dumps({'success': False, 'error': 'Needs title or username'}), 404
  group = Group(
      title=post_body.get('text'),
      admin=post_body.get('username'),
      info=post_body.get('info')
  )
  db.session.add(group)
  db.session.commit()
  return json.dumps({'success': True, 'data': group.serialize()}), 201


@app.route('/api/group/<int:group_id>/', methods=['DELETE'])
def delete_group(group_id):
    """Delete specified group"""
    group = Group.query.filter_by(id=group_id).first()
    if group is not None:
        db.session.delete(group)
        db.session.commit()
        return json.dumps({'success': True, 'data': group.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Group not found!'}), 404

@app.route('/api/group/<int:group_id>/', methods=['DELETE'])
def add_admin(group_id, user_id):
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        return json.dumps({'success': False, 'error': 'Group not found!'}), 404
    
    admin = User.query.filter_by(id=user_id).first()
    if admin is None:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404
    if admin in group.admins:
        return json.dumps({'success': False, 'error': 'User is already an Admin!'}), 404
    group.admins.append(admin)
    admin.admin_groups.append(group)
    db.session.commit()
    return json.dumps({'success': True, 'data': group.serialize()}), 201

@app.route('/api/group/<int:group_id>/admin/<int:user_id>/', methods=['DELETE'])
def remove_admin(group_id, user_id):
    group = Group.query.filter_by(id=group_id).first()
    if group is not None:
        admin = User.query.filter_by(id=user_id, group_id=group_id).first()
        if admin is not None:
            if group not in admin.admin_groups:
                return json.dumps({'success': False, 'error': 'User is not an Admin!'}), 404
            group.admins.remove(admin)
            admin.admin_groups.remove(group)
            db.session.commit()
            return json.dumps({'success': True, 'data': {'group': group.serialize(), 'admin': admin.serialize()}}), 200
        return json.dumps({'success': False, 'error': 'Admin not found!'}), 404
    return json.dumps({'success': False, 'error': 'Group not found!'}), 404

@app.route('/api/group/<int:group_id>/members/', methods=['POST'])
def add_member(group_id):
    #TODO.
    #try:
        #res = userfuncs.join_group(group_id, user_id)
        #return json.dumps({'success': True, 'data': user_id}), 200
    return None #json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

@app.route('/group/<int:group_id>/add/', methods=['POST'])
def add_to_group(group_id):
  post_body = json.loads(request.data)
  group = Group.query.filter_by(id=group_id).first()

  if 'admin' in post_body:
    user = User.query.filter_by(id=post_body['admin']).first()
    group.admin.append(user)

  if 'member' in post_body:
    user = User.query.filter_by(id=post_body['member']).first()
    group.members.append(user)
  
  if 'event' in post_body:
    event = Event.query.filter_by(id=post_body['event']).first()
    group.events.append(user)

  db.session.commit()
  return json.dumps({'success': True, 'data': group.serialize()}), 201



@app.route('/api/group/<int:group_id>/members/', methods=['DELETE'])
def remove_member(group_id, user_id):
    #TODO
    #try:
        #userfuncs.leave_group(group_id, user_id)
        #return 
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

def add_event():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

def remove_event():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

def edit_description():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

def edit_website():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

@app.route('/api/group/<int:group_id>/', methods=['POST'])
def update_group(post_id):
  """Update the post specified by the user's text."""
  #TODO: admin verification
  # post = Post.query.filter_by(id=post_id).first()
  #if post is not None:
  # post_body = json.loads(request.data)
  # if 'text' in post_body:
  # post.text = post_body.get('text', post.text)
  # db.session.commit()
  # return json.dumps({'success': True, 'data': post.serialize()}), 200
  # return json.dumps({'success': False, 'error': 'Post not found!'}), 404


#######################################
# EVENTS ROUTES
@app.route('/api/events/', methods=['POST'])
def create_event():
  post_body = json.loads(request.data)
  title = post_body.get('title')
  group = post_body.get('group')
  date = {'MM': post_body.get('MM'), 'DD': post_body.get('DD'), 'YYYY': post_body.get('YYYY')}
  time = {'start': post_body.get('start'), 'end': post_body.get('end')}
  description = post_body.get('description')
  location = {'name': post_body.get('locname'), 'address': post_body.get('address')}

  if group is not None:
      host = Group.query.filter_by(id=group.id).first().admin

  if title is None or time['start'] is None or time['end'] is None:
      return json.dumps({'error': 'Please complete all required fields.'})

  event = Event(
      title = title,
      date = date,
      time = time,
      group = group,
      description = description,
      location = location
  )

  db.session.add(event)
  db.session.commit()
  return json.dumps({'success': True, 'data': event.serialize()}), 201

def add_event():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

def remove_event():
    #TODO
    return json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

@app.route('/event/<int:event_id>/add/', methods=['POST'])
def attend_event(event_id):
  event = Event.query.filter_by(id=event_id).first()
  if event is not None:
    post_body = json_loads(request.data)
    attendee = User.query.filter_by(id=post_body['user_id']).first()
    event.attendees.append(attendee)
    #attendee.events.append(event)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 200
  return json.dumps({'success': False, 'error': 'User not found!'}), 404


#######################################
# USERS ROUTES
@app.route('/api/users/', methods=['POST'])
def create_user():
    """Create new user specified by the input. -- MIGHT NOT BE NECESSARY BC "register" FUNCTION IN authentication.py"""
    post_body = json.loads(request.data)
    if 'text' not in post_body or 'username' not in post_body:
        return json.dumps({'success': False, 'error': 'Needs text or username'}), 404
    user = User(
        id=user_id,
        username=post_body['username'],
        #g_user = post_data['gid']
        )
    db.session.add(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 201

@app.route('/api/user/<int:user_id>/', methods=['POST'])
def edit_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        return json.dumps({'success': False, 'error': 'Group not found!'}), 404
    
    user = User.query.filter_by(id=user_id).first()
    if admin is None:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404
    if admin in group.admins:
        return json.dumps({'success': False, 'error': 'User is already an Admin!'}), 404
    group.admins.append(admin)
    admin.a_groups.append(group)
    db.session.commit()
    return json.dumps({'success': True, 'data': group.serialize()}), 201

@app.route('/api/user/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    #TODO
    pass

@app.route('/api/user/<int:user_id>/group/<int:group_id>/', methods=['POST'])
def join_group(group_id, user_id):
    """"""
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        return json.dumps({'success': False, 'error': 'Group not found!'}), 404
    
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404
    if user in group.members:
        return json.dumps({'success': False, 'error': 'User is already a Member!'}), 404
    group.members.append(user)
    user.m_groups.append(group)
    db.session.commit()
    return json.dumps({'success': True, 'data': group.members.serialize()}), 201

@app.route('/api/user/<int:user_id>/groups/<int:group_id>/', methods=['DELETE'])
def leave_group(group_id, user_id):
    group = Group.query.filter_by(id=group_id).first()
    if group is None:
        return json.dumps({'success': False, 'error': 'Group not found!'}), 404
    
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404
    if user not in group.members:
        return json.dumps({'success': False, 'error': 'User is not a Member!'}), 404
    group.members.remove(user)
    user.member_groups.remove(group)
    #? user.admin_groups.remove(group)
    db.session.commit()
    return json.dumps({'success': True, 'data': group.members.serialize()}), 201



#######################################



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)