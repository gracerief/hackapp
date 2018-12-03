import routes, userfuncs, gets
from routes import app
import json
from db import db, Group, Event, User
from flask import Flask, request

@app.route('/api/groups/', methods=['POST'])
def create_group():
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
def add_member(group_id, user_id):
    #TODO.
    #try:
        #res = userfuncs.join_group(group_id, user_id)
        #return json.dumps({'success': True, 'data': user_id}), 200
    return None #json.dumps({'success': False, 'error': 'Function not yet Implemented!'}), 404

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