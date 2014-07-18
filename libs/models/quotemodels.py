#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

def quote_key(name="default"):
    return db.Key.from_path('quotes', name)

class Quote(db.Model):
    quote = db.TextProperty(required=True)
    source = db.StringProperty()
    username = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def as_dict(self):
        time_fmt = '%c'
        d = {'quote': self.quote,
             'source': self.source,
             'username': self.username,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.created.strftime(time_fmt)}
        return d

