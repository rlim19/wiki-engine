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
from google.appengine.api import users


class Home(basehandler.BaseHandler):
    def get(self):
        quotes = Quote.query().fetch(limit = None)

        p = Page.query()
        all_pages = p.filter(Page.version == 1).order(-Page.last_modified)
        all_pages = all_pages.fetch(limit=None)
        logging.error(all_pages)

        if all_pages:
            pages = []
            for page in all_pages:
                recent_page = Page._by_path(page.path).get() #get the most recent!
                if recent_page not in pages:
                    pages.append(recent_page)
            #logging.error(pages)

            path_content = []
            for page in pages:
                if page is not None:
                    path, content = page.path, markdown(page.content)
                    path_content.append((path, content))
        else:
            path_content = ''

        if quotes:
            choosen_quote = random.choice(quotes)
            source = choosen_quote.source
            quote = choosen_quote.quote
        else:
            quote = "We share, because we are not alone"
            source = ""
        logging.error(path_content)

        self.render("home.html", 
                    quote = quote, source = source,
                    pages = path_content)


class PageJson(basehandler.BaseHandler):
    def get(self):
        pages, quotes, age = front_pages()
        pages_json = [p._as_dict() for p in pages]
        return self.render_json(pages_json)

class QuoteJson(basehandler.BaseHandler):
    def get(self):
        pages, quotes, age = front_pages()
        quotes_json= [q._as_dict() for q in quotes]
        return self.render_json(quotes_json)


class EditPage(basehandler.BaseHandler):
    def get(self, path):
        if not self.user and not self.useradmin:
            self.redirect('/login')

        v = self.request.get('v')
        p = None
        if v:
            #logging.error('version: ' + v)
            if v.isdigit():
                #logging.error("hit DB query")
                p = Page._by_version(int(v), path).get()

            #if not page:
            #    return self.notfound()

        else:
            p = Page._by_path(path).get()

        self.render("edit.html", path=path , page=p)

    def post(self, path):
        if not self.user and not self.useradmin:
            self.error(400)
            return 

        content = self.request.get('content')

        if path and content:
            old_page = Page._by_path(path).get()
            if not old_page:
                version = 1 # initialize the page with version 1
            elif old_page.content == content:
                version = old_page.version
            elif old_page.content != content:
                version  = old_page.version + 1

            p = Page(parent = Page._parent_key(path),
                     username = self.uname,
                     path = path,
                     content = content, 
                     version = version)
            p.put()
            time.sleep(1)

            self.redirect(path)
        else:
            logging.error("content needed!")
            error="content needed!"
            self.render("edit.html", path=path, error=error)


class HistoryPage(basehandler.BaseHandler):
    def get(self, path):
        q = Page._by_path(path)
        posts = q.fetch(limit = None)

        if posts:
            self.render("history.html", path=path, posts=posts)
        else:
            #self.redirect("/_edit" + path)
            self.redirect("/")

class WikiPage(basehandler.BaseHandler):
    def get(self, path):
        v = self.request.get('v') # get the requested version
        p = None
        if v:
            if v.isdigit():
                logging.error("version:"+ v)
                p = Page._by_version(int(v), path).get()
                content = markdown(p.content)
            if not p:
                return self.notfound()
        else:
            p = Page._by_path(path).get()
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
        if self.user or self.useradmin: 
            self.render("addquote.html") 
        else: self.redirect('/login')  
    def post(self): 
        if self.user or self.useradmin: 
            quote = self.request.get('content') 
            source = self.request.get('source')

            if quote:
                q = Quote(parent = Quote._parent_key(),
                          quote = quote, source=source,
                          username = self.uname)
                q.put()
                self.redirect('/thankyou')
            else:
                logging.error('No Content')
                error = "Add a quote please!"
                self.render("addquote.html", error=error)

class Thankyou(basehandler.BaseHandler):
    def get(self):
        if self.user or self.useradmin:
            self.render("thankyou.html", name = self.uname)

class DeletePage(basehandler.BaseHandler):
    def get(self, path):
        keys_ = Page.query().filter(Page.path == path).fetch(keys_only = True)
        ndb.delete_multi(keys_)
        self.redirect('/?')

class DeleteVersionPage(basehandler.BaseHandler): 
    def get(self, path): 
        v = int(self.request.get('v')) 
        if not self.useradmin and not v: 
            self.error(400) 
            return

        key_ = Page.query(Page.path == path, Page.version == v).fetch(keys_only = True)
        ndb.delete_multi(key_)
        self.redirect('/_history' + path)
