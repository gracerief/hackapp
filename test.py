import unittest
import json
import requests

# NOTE: Make sure you run 'pip install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = 'http://localhost:5000'
BODY = {'text': 'Hello, World!', 'username': 'Megan'}
USER1 = {'username':'gkr9'}
EVENT1 = {'title':'fake!'}


class TestRoutes(unittest.TestCase):

    def test_get_initial_groups(self):
        res = requests.get(LOCAL_URL + '/api/groups/')
        assert res.json()['success']

    def test_create_group(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group = res.json()['data']
        assert res.json()['success']
        assert group['text'] == 'Hello, World!'
        assert group['username'] == 'Megan'
        assert group['score'] == 0

    def test_get__group(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group = res.json()['data']

        res = requests.get(LOCAL_URL + '/api/group/' + str(group['id']) + '/')
        assert res.json()['data'] == group

    def test_edit_group(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group_id = res.json()['data']['id']
        res = requests.post(LOCAL_URL + '/api/group/' + str(group_id) + '/',
                            data=json.dumps({'text': 'New text'}))
        assert res.json()['success']

        res = requests.get(LOCAL_URL + '/api/group/' + str(group_id) + '/')
        assert res.json()['data']['text'] == 'New text'

    def test_delete_group(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group_id = res.json()['data']['id']
        res = requests.delete(LOCAL_URL + '/api/group/' + str(group_id) + '/')
        assert res.json()['success']

    def test_group_comment(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group_id = res.json()['data']['id']
        comment = {'text': 'First comment', 'username': 'Megan'}
        res = requests.post(LOCAL_URL + '/api/group/' + str(group_id) + '/comment/',
                            data=json.dumps(comment))
        assert res.json()['success']

        res = requests.get(LOCAL_URL + '/api/group/' + str(group_id) + '/comments/')
        assert res.json()['success']
        comments = res.json()['data']
        assert len(comments) == 1
        assert comments[0]['text'] == 'First comment'
        assert comments[0]['username'] == 'Megan'

    def test_get_invalid_group(self):
        res = requests.get(LOCAL_URL + '/api/group/1000/')
        assert not res.json()['success']

    def test_edit_invalid_group(self):
        res = requests.post(LOCAL_URL + '/api/group/1000/',
                            data=json.dumps({'text': 'New text'}))
        assert not res.json()['success']

    def test_delete_invalid_group(self):
        res = requests.delete(LOCAL_URL + '/api/group/1000/')
        assert not res.json()['success']

    def test_get_comments_invalid_group(self):
        res = requests.get(LOCAL_URL + '/api/group/1000/comments/')
        assert not res.json()['success']

    def test_group_invalid_comment(self):
        res = requests.post(LOCAL_URL + '/api/group/1000/comment/', data=json.dumps(BODY))
        assert not res.json()['success']

    def test_group_id_increments(self):
        res = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group_id = res.json()['data']['id']

        res2 = requests.post(LOCAL_URL + '/api/groups/', data=json.dumps(BODY))
        group_id2 = res2.json()['data']['id']

        assert group_id + 1 == group_id2


if __name__ == '__main__':
    unittest.main()
