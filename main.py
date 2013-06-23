#!/usr/bin/env python
#
# Created by: Simon Brunet 2013-06-23
#
# Abstract:
#   Main
#
###############################################################################

import os, sys
# Setup the env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Utilities')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Application')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Db')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Cache')))

import webapp2
import jinja2
import re
import json

import Hashing
import Db
import Memcache

import logging

DEBUG = True

jinjaEnv = jinja2.Environment(autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))) 

# Memcache instance
memcache = Memcache.Memcache()

FRONT_KEY = 'WELCOME'

# Generic methods
def StripKey(key):
    if key == '/':  #Front page
        key = FRONT_KEY
    else:
        key = key[1:] #Strip the '/'
        key = key.split('/')[0] #Strip trailing '/' if any
    return key

def GetWikiEntry(key, update = False):
    query = Db.Query("Entry").order('-created').filter('name =', key).get
    return memcache.Get(key, query, update)

# Basic Handler
class Handler(webapp2.RequestHandler):
    def Write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)
        
    def WriteJson(self, data):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.Write(json.dumps(data))

    def RenderStr(self, template, **params):
        t = jinjaEnv.get_template(template)
        return t.render(params)
    
    def Render(self, template, **kwargs):
        self.Write(self.RenderStr(template, **kwargs))
        
    def SetCookie(self, cookie):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers.add_header('Set-Cookie', cookie)
        
    def DeleteCookie(self, cookie):
        self.response.delete_cookie(cookie)
        
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user = self.request.cookies.get('user', "")
        if user:
            user = user.split('|')[1]
        self.user = user

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'
        
class WikiPage(Handler):
    def get(self, key):
        key = StripKey(key)
        wiki = GetWikiEntry(key)
        if key == FRONT_KEY:
            if not wiki:  #Just for the first time
                wiki = Db.Put("Entry", txt = "<h2>Welcome</h2>", name = key)
                GetWikiEntry(key, True) #Refresh Memcache
            key = ""
        if not wiki:
            if not self.user:
                self.redirect('/login') # Must be logged in to edit
            else:
                self.redirect('/_edit/' + key)
            return
        self.Render("view.html", wiki=wiki.txt, user = self.user, entry = key)
        
class EditPage(Handler):
    def get(self, key):
        if not self.user:
            self.redirect('/login')  # For the smart ones...
            return
        key = StripKey(key)
        wiki = GetWikiEntry(key)
        if key == FRONT_KEY:
            key = ""
        if not wiki:
            txt = ""
        else:
            txt = wiki.txt
        self.Render("edit.html", txt = txt, user = self.user, entry=key)
        
    def post(self, key):
        key = StripKey(key)
        txt = self.request.get("content")
        wiki = Db.Put("Entry", txt = txt, name = key)
        GetWikiEntry(key, True) #Refresh Memcache
        if key == FRONT_KEY:
            key = ""
        self.redirect('/' + key)
    

class Signup(Handler):

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

    def renderSignup(self, **kwargs):
        self.Render("signup.html", **kwargs)

    def get(self):
        self.renderSignup()

    def post(self):
        user = str(self.request.get("username"))
        password = str(self.request.get("password"))
        verify = str(self.request.get("verify"))
        email = str(self.request.get("email"))
        
        if not user or not self.USER_RE.match(user):
            self.renderSignup(errorUser = "That's not a valid username.", user=user)
            return 
        if not password or not self.PASS_RE.match(password):
            self.renderSignup(errorPass = "That's not a valid password.", user=user)
            return
        if not verify or password != verify:
            self.renderSignup(errorVerify = "Your passwords didn't match.", user=user)
            return
        if email and not self.EMAIL_RE.match(email):
            self.renderSignup(errorEmail = "That's not a valid email.", email=email, user=user)
            return
        if Db.Query("User").filter('user =',user).get():
            self.renderSignup(errorUser = "User already choosen.", email=email, user=user)
            return

        Db.Put("User", user=user, password=Hashing.GetPwHash(password), email=email)
        # TODO brunets 2013-06-23 Memcache users
        self.SetCookie('user=%s' % Hashing.GetHash(user))
        self.redirect('/')

class Login(Handler):
    def get(self):
        self.Render("login.html")

    def post(self):
        user = str(self.request.get("username"))
        password = self.request.get("password")

        userData = Db.Query("User").filter('user =',user).get()
        if not userData:
            self.Render("login.html", error = 'This user does not exists', user=user)
            return
        if not Hashing.ValidPw(password, userData.password):
            self.Render("login.html", error = 'Incorrect Password', user=user)
            return

        self.SetCookie('user=%s' % Hashing.GetHash(user))
        self.redirect('/')

class Logout(Handler):
    def get(self):
        self.DeleteCookie("user")
        self.redirect('/')

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/_edit' + PAGE_RE, EditPage),
                               (PAGE_RE, WikiPage),
                               ],
                              debug=DEBUG)
