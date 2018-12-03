import routes, userfuncs, gets
from routes import app
import json
from db import db, Group, Event, User
from flask import Flask, request

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


