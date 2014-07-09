#! /usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from google.appengine.ext import db
from basehandler import basehandler
from libs.utils.utils import *
from libs.models.usermodels import *


### handlers ###

class Signup(basehandler.BaseHandler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.render('signup.html', next_url = next_url)
    def post(self):
        have_error = False
        next_url = str(self.request.get('next_url'))
        if not next_url or next_url.startwith('/login'):
            next_url = '/'

        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username, 
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
        elif self.password == self.username:
            params['error_password'] = "Password can't be your username."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            u = User.by_name(self.username)
            if u:
                msg = 'That user already exists.'
                params = {'username': self.username, 'error_username': msg}
                self.render('signup.html', **params)
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()
                self.login(u)
                self.redirect(next_url)

            
class Welcome(basehandler.BaseHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')

class Login(basehandler.BaseHandler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.render('login.html', next_url = next_url)
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        next_url = str(self.request.get('next_url'))
        if not next_url or next_url.startwith('/login'):
            next_url = '/'

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect(next_url)
        else:
            msg = 'invalid login'
            self.render('login.html', error_login = msg)

class Logout(basehandler.BaseHandler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.logout()
        # get to the previous page before log out
        self.redirect(next_url)
