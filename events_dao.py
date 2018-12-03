from sqlalchemy_imageattach.context import store_context

with store_context(store):
    with open('image_to_attach.jpg') as f:
        entity.picture.from_file(f)

def event_active():
    current_time = datetime.datetime.now() + datetime.timedelta(days=1)
    
    event = Event.query.filter_by(id=event_id).first()
    if event is not None:

    current_time = datetime.datetime.now() + datetime.timedelta(days=1)
    event_time = event.time

def create_event():
    #put in routes.py
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


def set_picture(request, event_id):
    try:
        event = Event.query.get(id=event_id)
        with store_context(store):
            event.photo.from_file(request.files['photos'])
    except Exception:
        db.session.rollback()
        raise
    db.session.commit()