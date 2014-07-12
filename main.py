#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

from webapp2_extras import routes
from wikiengine import wiki_handlers
from wikiengine import quote_handlers
from users import users_handlers

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

#PAGE_RE = r'(/(?:[a-zA-Z0-9]+/?)*)'
PAGE_RE = r'(/.*)'
app = webapp2.WSGIApplication([
       ('/testtemp', wiki_handlers.TestTemp),
       ('/signup', users_handlers.Signup),
       ('/login', users_handlers.Login),
       ('/logout', users_handlers.Logout),
       ('/quotes', quote_handlers.QuotePage),
       ('/addquote', quote_handlers.AddQuote),
       ('/thankyou', quote_handlers.Thankyou),
       ('/?', wiki_handlers.Home),
       ('/_edit' + PAGE_RE, wiki_handlers.EditPage),
       ('/_history' + PAGE_RE, wiki_handlers.HistoryPage),
       (PAGE_RE, wiki_handlers.WikiPage),
      ], debug=DEBUG)
