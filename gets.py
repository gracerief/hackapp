import routes, userfuncs, gets
from routes import app
import json
from db import db, Group, Event, User
from flask import Flask, request

@app.route('/api/groups/')
def get_groups():
    """Return all currently stored groups."""
    groups = Group.query.all()
    res = {'success': True, 'data': [group.serialize() for group in groups]}
    return json.dumps(res), 200

@app.route('/api/group/<int:group_id>/')
def get_group(group_id):
    """Return the group specified by the group id."""
    group = Group.query.filter_by(id=group_id).first()
    if group is not None:
        return json.dumps({'success': True, 'data': group.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Group not found!'}), 404

@app.route('/api/users/')
def get_users():
    """Return all currently stored users."""
    users = User.query.all()
    res = {'success': True, 'data': [user.serialize() for user in users]}
    return json.dumps(res), 200

@app.route('/api/user/<int:user_id>/')
def get_user(user_id):
    """Return the user specified by the user id."""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        return json.dumps({'success': True, 'data': user.serialize()}), 200
    return json.dumps({'success': False, 'error': 'User not found!'}), 404


@app.route('/api/events/')
def get_events():
    """Return all currently stored events."""
    events = Event.query.all()
    res = {'success': True, 'data': [event.serialize() for event in events]}
    return json.dumps(res), 200

@app.route('/api/event/<int:event_id>/')
def get_event(event_id):
    """Return the event specified by the event id."""
    event = Event.query.filter_by(id=event_id).first()
    if event is not None:
        return json.dumps({'success': True, 'data': event.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Event not found!'}), 404

@app.route('/api/user/<int:user_id>/groups/')
def get_user_groups(user_id, all_groups=True):
    """Return the groups of which a user is a member."""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        if all_groups:
            groups = user.member_groups
            return json.dumps({'success': True, 'data': groups.serialize()}), 200
        groups = user.admin_groups
        return json.dumps({'success': True, 'data': groups.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Event not found!'}), 404
