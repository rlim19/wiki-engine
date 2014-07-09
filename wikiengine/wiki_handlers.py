#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from libs.models.pagemodels import *
from libs.utils.utils import *
import logging
import urllib

def gray_style(lst):
    for n,x in enumerate(lst):
        if n%2 == 0:
            yield x, ''
        else:
            yield x, 'gray'


class Index(basehandler.BaseHandler):
    def get(self):
        self.render('index.html')

class Home(basehandler.BaseHandler):
    def get(self):
        q = db.Query(Page)

        # get all the unique pages (version 1)
        pages= q.filter('version =', 1).order('-last_modified').fetch(limit=None)

        # filter for the most recent versions to be displayed
        recent_pages = []
        for page in pages:
            recent_page = Page.by_path(page.path).get() #get the most recent!
            if recent_page not in recent_pages:
                recent_pages.append(recent_page)
        
        self.render("home.html", pages=recent_pages)


class EditPage(basehandler.BaseHandler):
    def get(self, path):
        if not self.user:
            self.redirect('/login')

        v = self.request.get('v')
        p = None
        if v:
            #logging.error('version: ' + v)
            if v.isdigit():
                p = Page.by_version(int(v), path).get()

            if not p:
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
                version = 1
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
            self.redirect(path)
        else:
            error="content needed!"
            self.render("edit.html", path=path, error=error)


class HistoryPage(basehandler.BaseHandler):
    def get(self, path):
        q = Page.by_path(path)
        q.fetch(limit = 100)

        posts = list(q)
        if posts:
            self.render("history.html", path=path, posts=posts)
        else:
            self.redirect("/_edit" + path)

class WikiPage(basehandler.BaseHandler):
    def get(self, path):
        v = self.request.get('v')
        p = None
        if v:
            if v.isdigit():
                logging.error("version:"+ v)
                p = Page.by_version(int(v), path).get()
            if not p:
                return self.notfound()
        else:
            p = Page.by_path(path).get()
            logging.error("no version")

        if p:
            logging.error("there is a page")
            self.render("page.html", page=p, path=path)
        else:
            logging.error("there is NOT a page")
            self.redirect("/_edit" + path)
