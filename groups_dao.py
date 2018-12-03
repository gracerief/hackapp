# GROUPS DAO
from db import db, Group

def get_group_by_title(title):
    return Group.query.filter(Group.title == title).first()

def verify_credentials(email, password):
    optional_group = get_group_by_email(email)

    if optional_group is None:
        return False, None

    return optional_group.verify_password(password), optional_group
