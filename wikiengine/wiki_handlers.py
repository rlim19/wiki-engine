#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from libs.models.pagemodels import *
from libs.models.quotemodels import *
from libs.utils.utils import *
import logging
import urllib
from google.appengine.api import memcache
from datetime import datetime, timedelta
import time
from libs.utils.markdown2 import *
import random

class TestTemp(basehandler.BaseHandler):
    def get(self):
        self.render("edit_tmp.html")

def front_pages(update=False):
    """
    memcache the front_pages on the wiki home
    """

    memc = memcache.Client()
    key = "PAGES"

    #for i in xrange(1,10):
    while True:
        r = memc.gets(key)
        if r:
            pages, quotes, save_time = r
            age = (datetime.utcnow() - save_time). total_seconds()
        else:
            pages, quotes, age = None, None, 0
            #logging.error('Initialized')

        if pages is None or update:
            #logging.error('Hit DB query')

            p = db.Query(Page)
            q = db.Query(Quote)

            quotes = q.fetch(limit=None)

            # get all the unique pages (version 1)
            all_pages= p.filter('version =', 1).order('-last_modified')
            all_pages = all_pages.fetch(limit=None)

            # filter for the most recent versions to be displayed
            pages = []
            for page in all_pages:
                recent_page = Page.by_path(page.path).get() #get the most recent!
                if recent_page not in pages:
                    pages.append(recent_page)

            save_time = datetime.utcnow()
            memc.add(key, (pages, quotes, save_time))

        assert pages is not None, "Uninitialized pages"

        # check and set the cache (make sure that the cache stores the most recent pages)
        if memc.cas(key, (pages, quotes, save_time)):
            #logging.error('Test cas pass')
            break

    return pages, quotes, age

def age_str(age):
    s = 'Queried %s seconds ago'
    age = int(age)
    if age == 1:
        s = s.replace('seconds', 'second')
    return s % age


class Home(basehandler.BaseHandler):
    def get(self):
        pages, quotes, age = front_pages()

        path_content = []
        for page in pages:
            path, content = page.path, markdown(page.content)
            path_content.append((path, content))

        if quotes:
            choosen_quote = random.choice(quotes)
            source = choosen_quote.source
            quote = choosen_quote.quote
        else:
            quote = "We share, because we are not alone"
            source = ""

        self.render("home.html", 
                     quote=quote, source=source, 
                     pages=path_content, age=age_str(age))




class EditPage(basehandler.BaseHandler):
    def get(self, path):
        if not self.user:
            self.redirect('/login')

        v = self.request.get('v')
        p = None
        if v:
            #logging.error('version: ' + v)
            if v.isdigit():
                logging.error("hit DB query")
                p = Page.by_version(int(v), path).get()

            if not page:
                return self.notfound()
        
        else:
            p = Page.by_path(path).get()

        self.render("edit.html", path=path , page=p)

    def post(self, path):
        if not self.user:
            self.error(400)
            return 

        content = self.request.get('content')

        if path and content:
            old_page = Page.by_path(path).get()
            if not old_page:
                version = 1 # initialize the page with version 1
            elif old_page.content == content:
                version = old_page.version
            elif old_page.content != content:
                version  = old_page.version + 1


            p = Page(parent = Page.parent_key(path),
                     username = self.user.name,
                     path = path,
                     content = content, 
                     version = version)
            p.put()
            time.sleep(1)
            front_pages(update=True)

            self.redirect(path)
        else:
            logging.error("content needed!")
            error="content needed!"
            self.render("edit.html", path=path, error=error)


class HistoryPage(basehandler.BaseHandler):
    def get(self, path):
        q = Page.by_path(path)
        posts = q.fetch(limit = None)

        #posts = list(q)
        if posts:
            self.render("history.html", path=path, posts=posts)
        else:
            self.redirect("/_edit" + path)

class WikiPage(basehandler.BaseHandler):
    def get(self, path):
        v = self.request.get('v') # get the requested version
        p = None
        if v:
            if v.isdigit():
                logging.error("version:"+ v)
                p = Page.by_version(int(v), path).get()
                content = markdown(p.content)
            if not page:
                return self.notfound()
        else:
            p = Page.by_path(path).get()
            if p:
                content = markdown(p.content)
            else:
                content = p

        if p:
            self.render("page.html", content=content, path=path)
        else:
            self.redirect("/_edit" + path)

class AddQuote(basehandler.BaseHandler):
    def get(self):
        if self.user:
            self.render("addquote.html")
        else:
            self.redirect('/login')

    def post(self):
        if self.user:
            quote = self.request.get('content')
            source = self.request.get('source')

            if quote:
                q = Quote(parent=quote_key(), 
                          quote=quote, source=source, 
                          username=self.user.name)
                q.put()
                time.sleep(1)
                front_pages(update=True)
                self.redirect('/thankyou')
            else:
                logging.error('No Content')
                error = "Add a quote please!"
                self.render("addquote.html", error=error)

class Thankyou(basehandler.BaseHandler):
    def get(self):
        if self.user:
            self.render("thankyou.html", name=self.user.name)
