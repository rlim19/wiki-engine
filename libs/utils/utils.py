#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import hashlib
import string
import random
import hmac
from config import *
import cgi

def escape_html(s):
    return cgi.escape(s)


## validation signup
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}")
def valid_password(password):
    return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)

## cookies
def make_secure_val(val):
    return "%s|%s" %(val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

## salted and hashed password
def make_salt():
    return ''.join(random.sample(string.letters, 5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name+pw+salt).hexdigest()
    return '%s,%s'%(salt, h)

def valid_pw(name, pw, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name,pw,salt)

def gray_style(lst):
    for n,x in enumerate(lst):
        if n%2 == 0:
            yield x, ''
        else:
            yield x, 'gray'
