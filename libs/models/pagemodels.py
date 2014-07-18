#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from libs.utils.markdown2 import *

class Page(db.Model):
    path = db.StringProperty(required=True)
    username = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    version = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def parent_key(path):
        return db.Key.from_path('/root'+path, 'wikipages')

    @classmethod
    def by_path(cls, path):
        q = cls.all()
        q.ancestor(cls.parent_key(path))
        q.order("-version")
        return q

    @classmethod
    def by_id(cls, page_id, path):
        return cls.get_by_id(page_id, cls.parent_key(path))

    @classmethod
    def by_version(cls, version, path):
        q = cls.all()
        q.ancestor(cls.parent_key(path))
        q.filter("version =", version)
        return q

    def as_dict(self):
        time_fmt = '%c'
        d = {'path': self.path,
             'username': self.username,
             'content': markdown(self.content),
             'version': self.version,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.created.strftime(time_fmt)}
        return d
