#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import jinja2
import webapp2
import cgi
import hmac
import json
from libs.utils.utils import *
from libs.models.usermodels import *
from libs.models.pagemodels import *
from google.appengine.api import users

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'),
                               autoescape=True)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['admin_logout'] = users.create_logout_url('/')
        params['gray_style'] = gray_style
        params['admin'] = self.useradmin
        t = jinja_env.get_template(template)
        return t.render(params)

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
                'Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))
    
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # check user_id cookie for every request (every instance creation)
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User._by_id(int(uid))
        self.useradmin = users.is_current_user_admin() and users.get_current_user()

        if self.useradmin: self.uname = users.get_current_user().nickname()
        if self.user: self.uname = self.user.name
        #self.isadmin = users.is_current_user_admin()
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header(
                'Set-Cookie', 'user_id=; Path=/')
    def notfound(self):
        self.error(404)
        self.write('<h1>404: Not Found</h1>, Sorry your page does not exist')

    def next_url(self):
        self.request.headers.get('referer', '/')
