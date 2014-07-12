#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

def quote_key(name="default"):
    return db.Key.from_path('quotes', name)

class Quote(db.Model):
    quote = db.TextProperty(required=True)
    source = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

