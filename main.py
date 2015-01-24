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

PAGE_RE = r'(/(?:[a-zA-Z0-9]+/?)*)'
app = webapp2.WSGIApplication([
       ('/admin/?', wiki_handlers.Home),
       ('/admin/_delete' + PAGE_RE, wiki_handlers.DeletePage),
       ('/admin/_deleteV' + PAGE_RE, wiki_handlers.DeleteVersionPage),
       ('/pages.json', wiki_handlers.PageJson),
       ('/quotes.json', wiki_handlers.QuoteJson),
       ('/signup', users_handlers.Signup),
       ('/login', users_handlers.Login),
       ('/logout', users_handlers.Logout),
       ('/quotes', quote_handlers.QuotePage),
       ('/addquote', wiki_handlers.AddQuote),
       ('/thankyou', wiki_handlers.Thankyou),
       ('/?', wiki_handlers.Home),
       ('/_edit' + PAGE_RE, wiki_handlers.EditPage),
       ('/_history' + PAGE_RE, wiki_handlers.HistoryPage),
       (PAGE_RE, wiki_handlers.WikiPage),
      ], debug=DEBUG)
