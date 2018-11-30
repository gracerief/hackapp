from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Group(db.Model):
  __tablename__ = 'group'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Integer, nullable=False)
  admin = db.Column(db.String, nullable=False)
  #website = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  members = db.relationship('Member', cascade='delete')
  events = db.relationship('Event', cascade='delete')

  def __init__(self, **kwargs):
    self.title = kwargs.get('title', '')
    self.admin = kwargs.get('admin', '')
    self.description = kwargs.get('description', '')
    self.website = kwargs.get('website', '')
    #members = kwargs.get (members) or (user where username is self.admin)
    #events = kwargs.get (events)

  def serialize(self):
    return {
        'id': self.id,
        'title': self.title,
        'admin': self.admin,
        'info': {
            'description': self.description,
            'website': self.website
        }
        #'members': self.members
        #'events': self.events
    }

class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Integer, nullable=False)
  text = db.Column(db.String, nullable=False)
  username = db.Column(db.String, nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

  def __init__(self, **kwargs):
    self.score = kwargs.get('score', 0)
    self.text = kwargs.get('text', '')
    self.username = kwargs.get('username', '')
    self.post_id = kwargs.get('post_id')

  def serialize(self):
    return {
        'id': self.id,
        'score': self.score,
        'text': self.text,
        'username': self.username
    }


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, nullable=False)
  groups = db.relationship('Group', cascade='delete')

  def __init__(self, **kwargs):
    self.score = kwargs.get('score', 0)
    self.text = kwargs.get('text', '')
    self.username = kwargs.get('username', '')
    self.post_id = kwargs.get('post_id')

  def serialize(self):
    return {
        'id': self.id,
        'score': self.score,
        'text': self.text,
        'username': self.username
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
    