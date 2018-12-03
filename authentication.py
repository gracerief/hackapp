from google.oauth2 import id_token
from google.auth.transport import requests
import routes, userfuncs, gets
from routes import app
import json
from db import db, Group, Event, User
from flask import Flask, request






@app.route('/api/users/', methods=['POST'])
def auth_user():
    # (Receive token by HTTPS POST)
    # ...

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        user_id = id_info['sub']
    except ValueError:
        # Invalid token
        pass
    
    g_user = User.query.filter_by(id=user_id).first()

    if user is not None:
        #login
        pass
    else:
        @app.route('/api/register', methods=['POST'])
        def register():
            post_body = json.loads(request.data)
            #if 'title' not in post_body or 'username' not in post_body:
                #return json.dumps({'success': False, 'error': 'Needs title or username'}), 404
            
            user = User(
                id=user_id,
                username=post_body['username'],
                g_user = id_info
            )

            try:
                db.session.add(user)
                db.session.commit()
                status = 'success'
            except:
                status = 'this user is already registered'
            db.session.close()
            return jsonify({'result': status})

