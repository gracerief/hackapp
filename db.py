from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os
db = SQLAlchemy()

class Group(db.Model):
  __tablename__ = 'group'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Integer, nullable=False)
  admin = db.relationship('User', back_populates="admin_groups", nullable=False)
  #website = db.Column(db.String, nullable=False)
  description = db.Column(db.String)
  members = db.relationship('User', back_populates="member_groups")
  events = db.relationship('Event', back_populates="info.group")

  def __init__(self, **kwargs):
    self.title = kwargs.get('title', '')
    self.admin = kwargs.get('admin')
    self.info.description = kwargs.get('description', '')
    self.info.website = kwargs.get('website', '')
    self.members = kwargs.get('members')
    self.events = kwargs.get('events')

  def serialize(self):
    return {
        'id': self.id,
        'title': self.title,
        'admin': self.admin,
        'info': {
            'description': self.description,
            'website': self.website
        },
        'members': self.members,
        'events': self.events
    }

class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Integer, nullable=False)
  time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  attendees = db.relationship('User', back_populates="events")
  group = db.relationship('Group', back_populates="events")
  host = db.relationship('User', back_populates="events")
  #TODO: LOCATION
  locname = db.Column(db.String)
  address = db.Column(<GOOGLE MAPS ADDRESS>)
  #TODO: EVENT PHOTO
  #rel update -- group = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
  photo = db.Column(db.Image)

  def __init__(self, **kwargs):
    self.title = kwargs.get('title', '')
    self.date = kwargs.get('date')
    self.time = kwargs.get('time')
    self.attendees = kwargs.get('attendees')
    self.group = kwargs.get('group')
    if self.group is not None:
      #if affiliated with a group, all group admins are hosts
      admins = get_group(self.group)['data']['admins']
      self.host = admins
    else:
      #else, host is user creating event
      self.host = kwargs.get('host')
    self.location = {}
    self.location['name'] = kwargs.get('locname')
    self.location['address'] = kwargs.get('address')
    

  def serialize(self):
    return {
        'id': self.id,
        'title': self.title,
        'date': self.date,
        'time': self.time,
        'attendees': self.attendees,
        'info': {
          'group': self.info['group'],
          'host': self.info['host']
        }
        'location': {
          'name': self.location['name'],
          'address': self.location['address']
        }
    }


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  # User information
  email = db.Column(db.String, nullable=False, unique=True)
  password_digest = db.Column(db.String, nullable=False)

  # Session information
  session_token = db.Column(db.String, nullable=False, unique=True)
  session_expiration = db.Column(db.DateTime, nullable=False)
  update_token = db.Column(db.String, nullable=False, unique=True)

  username = db.Column(db.String, nullable=False)
  groups = db.relationship('Group', cascade='delete')
  admin_groups = db.relationship('Group', back_populates="admins")
  member_groups = db.relationship('Group', back_populates="members")
  events = db.relationship('Event', back_populates="attendees")

  # comments = db.relationship('Comment', cascade='delete')
  # post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

  def __init__(self, **kwargs):
    #self.username = kwargs.get('username', '')
    #g_user = ()
    #self.email = kwargs.get('email')
    self.admin_groups = kwargs.get('admin_groups')
    self.member_groups = kwargs.get('member_groups')
    self.events = kwargs.get('events')

    self.email = kwargs.get('email')
    self.password_digest = bcrypt.hashpw(kwargs.get('password').encode('utf8'), bcrypt.gensalt(rounds=13))
    self.renew_session()

  def serialize(self):
    return {
        'id': self.id,
        #'username': self.username,
        'email': self.email,
        'admin_groups': self.admin_groups,
        'member_groups': self.member_groups,
        'events': self.events
    }
  
  def join_group(self, group_id, admin=False, organizer=False):
    #add group to self.groups
    #if admin, self.groups[group][admin] = True
    #if organizer, self.groups[group][organizer] = True
    group = Group.query.filter_by(id=group_id).first()
    self.groups.insert(group)
    if admin:
      self.groups[group][admin] = True
    if organizer:
      self.groups[group][organizer] = True

  # Used to randomly generate session/update tokens
  def _urlsafe_base_64(self):
      return hashlib.sha1(os.urandom(64)).hexdigest()

  # Generates new tokens, and resets expiration time
  def renew_session(self):
      self.session_token = self._urlsafe_base_64()
      self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
      self.update_token = self._urlsafe_base_64()

  def verify_password(self, password):
      return bcrypt.checkpw(password.encode('utf8'), self.password_digest)

  # Checks if session token is valid and hasn't expired
  def verify_session_token(self, session_token):
      return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

  def verify_update_token(self, update_token):
      return update_token == self.update_token
    