#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from libs.utils.utils import *

# create the ancestry key (for consistency)
class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_visit = ndb.DateTimeProperty(auto_now = True)

    @staticmethod
    def _parent_key(group = "default"):
        return ndb.Key('users', group)

    @classmethod
    def _by_id(cls, uid):
        return cls.get_by_id(uid, cls._parent_key())

    @classmethod
    def _by_name(cls, name):
        u = cls.query(ancestor = cls._parent_key())
        u = u.filter(cls.name == name).get()
        return u

    @classmethod
    def _register(cls, name, pw, email):
        pw_hash = make_pw_hash(name,pw)
        return cls(parent = cls._parent_key(),
                   name = name,
                   pw_hash = pw_hash,
                   email = email)

    @classmethod
    def _login(cls, name, pw):
        u = cls._by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
