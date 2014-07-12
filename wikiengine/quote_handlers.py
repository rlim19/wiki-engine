#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from libs.models.quotemodels import *
from google.appengine.api import memcache
from libs.utils.markdown2 import *
import random
from datetime import datetime, timedelta
import logging
import time

def age_str(age):
    s = 'Queried %s seconds ago'
    age = int(age)
    if age == 1:
        s = s.replace('seconds', 'second')
    return s % age

def get_quotes(update=False):
    memc = memcache.Client()
    key = "QUOTES"

    for i in xrange(1,10):
        r = memc.gets(key)
        if r:
            quotes, save_time = r
            age = (datetime.utcnow() - save_time).total_seconds()
        else:
            quotes, age = None, 0
            logging.error("Initialized")

        if quotes is None or update:
            logging.error("DB Query")
            q = db.Query(Quote)
            quotes = q.fetch(limit=None)
            save_time = datetime.utcnow()

            memc.add(key, (quotes, save_time))

        if memc.cas(key, (quotes, save_time)):
            logging.error("cas test pass")
            break

    return quotes, age

class QuotePage(basehandler.BaseHandler):
    def get(self):
        quotes, age = get_quotes()
        if quotes:
            quote = random.choice(quotes)
            quote = markdown(quote.quote)
            logging.error(quote)
        else:
            quote = "<blockquote>We share, because we are not alone</blockquote>"
        self.render("quote.html", quote=quote, age=age_str(age))

class AddQuote(basehandler.BaseHandler):
    def get(self):
        if self.user:
            self.render("addquote.html")
        else:
            self.redirect('/login')

    def post(self):
        if self.user:
            quote = self.request.get('content')
            if quote:
                q = Quote(parent=quote_key(), 
                          quote=quote, source=self.user.name)
                q.put()
                time.sleep(1)
                get_quotes(update=True)
                self.redirect('/thankyou')
            else:
                error = "Add a quote please!"
                self.render("addquote.html", error=error)

class Thankyou(basehandler.BaseHandler):
    def get(self):
        self.render("thankyou.html")
