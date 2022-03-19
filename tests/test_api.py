# """
# Test API
# """
# import unittest
# from flask import json
# from app import db, create_app
# from app.models import Role, User
# from base64 import b64encode
#
#
# class APITestCase(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app('testing')
#         self.app_context = self.app.app_context()
#         self.app_context.push()
#         db.create_all()
#         Role.insert_roles()
#         self.client = self.app.test_client()
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#         self.app_context.pop()
#
#     @staticmethod
#     def get_api_headers(username, password):
#         return {
#             'Authorization': 'Basic' + b64encode((username + ':' + password).encode('utf-8')).decode('utf-8'),
#             'Accept': 'application/json',
#             'Content-Type': 'application/json'
#         }
#
#     def test_404(self):
#         response = self.client.get('/wrong/url', headers=self.get_api_headers('email', 'password'))
#         self.assertEqual(response.status_code, 404)
#         json_response = json.loads(response.get_data(as_text=True))
#         self.assertEqual(json_response['error'], 'not found')
#
#     def test_no_auth(self):
#         response = self.client.get('/api/v1/posts', content_type='application/json')
#         self.assertEqual(response.status_code, 308)     # 状态码依据 methods 和 是否回传而定
#
#     def test_bad_auth(self):
#         # add a user
#         r = Role.query.filter_by(name='User').first()
#         self.assertIsNotNone(r)
#         u = User(email='john@example.com', password='cat', confirmed=True, role=r)
#         db.session.add(u)
#         db.session.commit()
#
#         # authenticate with bad password
#         response = self.client.get(
#             '/api/v1/posts/',
#             headers=self.get_api_headers('john@example.com', 'dog'))
#         self.assertEqual(response.status_code, 401)
#
#     def test_posts(self):
#         # 添加一个用户
#         r = Role.query.filter_by(name='User').first()
#         self.assertIsNotNone(r)
#         u = User(email='john@examply.com', password='cat', confirmed=True, role=r)
#         db.session.add(u)
#         db.session.commit()
#
#         # write an empty post
#         response = self.client.post('/api/v1/posts/',
#                                     headers=self.get_api_headers('john@example.com', 'cat'),
#                                     data=json.dumps({'body': ''}))
#         self.assertEqual(response.status_code, 401)
#
#         # write a post
#         response = self.client.post('/api/v1/posts/',
#                                     headers=self.get_api_headers('john@example.com', 'cat'),
#                                     data=json.dumps({'body': 'body of the *blog* post'}))
#         self.assertEqual(response.status_code, 401)
#         url = response.headers.get('Location')
#         try:
#             self.assertIsNotNone(url)
#             self.assertIsNone(url)
#         except Exception as e:
#             print(e)
#
#         # 获取刚 post的文章
#         response = self.client.get(
#             url,
#             headers=self.get_api_headers('john@example.com', 'cat'))
#         self.assertEqual(response.status_code, 200)
#         json_response = json.loads(response.get_data(as_text=True))     # as_text使得 回传为字符串
#         self.assertEqual('http://localhost' + json_response['url'], url)
#         self.assertEqual(json_response['body'], 'body of the *blog* post')
#         self.assertEqual(json_response['body_html'], '<p>body of the <em>blog</em> post<p>')
#         # json_post = json_response
