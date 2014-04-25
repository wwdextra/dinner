#! /usr/bin/python
# encoding=utf-8
# test_auth.py
# ~~~~~~~~~~~~
# author: Michael Fan
# Description: Test the login function

import random
import unittest
import requests

no_error = 0
http_ok = 200
http_forbiden = 403
email = 'dd'
ok_password = 'ss'
xsrf = '18bbdbc57c704eb99e86a9e6446a3360' # A correct Tornado xsrf string

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_index_page(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        login_url = 'http://localhost:9000/login'
        data = {'email': email, 'password': ok_password,'_xsrf': xsrf}
        r = requests.post(login_url, data=data)
        self.assertEqual(r.json().get('ec'), no_error)

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))


# todo: test can't login        


if __name__ == '__main__':
    unittest.main()
    login_url = 'http://localhost:9000/login'
    data = {'email': 'root@example.com', 'password': '111111','_xsrf': xsrf}
    r = requests.post(login_url, data=data)
    # self.assertEqual(r.json(encoding='UTF-8').get('ec'), no_error)
    print r.content
    print r.status_code
