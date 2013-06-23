#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import cgi
import os
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

form="""
    <form method="post" action="/testform">
        <input name="q">
        <input type="submit">
    </form>
    """

ROT13="""
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;"
                >%(Text)s</textarea>
      <br>
      <input type="submit">
    </form>
    """

def Rot13(s):
    return s.encode('rot13')

def HtmlEscaping(s):
    return cgi.escape(s, quote=True)

class ROT13Handler(webapp2.RequestHandler):
    def __WriteForm(self, s = ""):
        self.response.write(ROT13 % {"Text" :s})
    
    def get(self):
        self.__WriteForm()

    def post(self):
        self.__WriteForm(HtmlEscaping(Rot13(self.request.get('text'))))

class SignupHandler(webapp2.RequestHandler):

    ERR_USER = "That's not a valid username."
    ERR_PASS = "That wasn't a valid password."
    ERR_VERIFY = "Your passwords didn't match."
    ERR_EMAIL = "That's not a valid email."

    path = os.path.join(os.path.dirname(__file__), 'Signup.html')
    f = open(path, 'r')
    Signup = f.read()
    SignupClean = Signup % {"User":"",
                            "ErrorUser":"",
                            "Pass":"",
                            "ErrorPass":"",
                            "Verify":"",
                            "ErrorVerify":"",
                            "Email":"",
                            "ErrorEmail":""}

    def WriteForm(self, form):
        self.response.out.write(form)

    def EditForm(self, form, field, text):
        return form % {field:HtmlEscaping(text)}

    def Get(self, what):
        return self.request.get(what)

    def IsValidUser(self):
        return USER_RE.match(self.Get('username'))

    def IsValidPass(self):
        return PASS_RE.match(self.Get('password'))

    def IsPassVerified(self):
        Pass = self.Get('password')
        Verify = self.Get('verify')
        return Pass == Verify

    def IsValidEmail(self):
        return EMAIL_RE.match(self.Get('email'))

    def get(self):
        self.WriteForm(self.SignupClean)

    def post(self):
        form = self.Signup
        Valid = True

        # Username
        form = self.EditForm(form, "User", self.Get('username'))
        if self.IsValidUser():
            form = self.EditForm(form, "ErrorUser", "")
        else:
            form = self.EditForm(form, "ErrorUser", self.ERR_USER)
            Valid = False

        # Password Verification
        if not self.IsPassVerified():
            form = self.EditForm(form, "ErrorVeriy", self.ERR_VERIFY)
            form = self.EditForm(form, "ErrorPass", "")
            form = self.EditForm(form, "Pass", "")
            form = self.EditForm(form, "Verify", "")
            Valid = False
        else:
            # Password
            if not self.IsPassVerified():
                form = self.EditForm(form, "ErrorPass", self.ERR_PASS)
                form = self.EditForm(form, "ErrorVerify", "")
                form = self.EditForm(form, "Pass", "")
                form = self.EditForm(form, "Verify", "")
                Valid = False
            else:
                form = self.EditForm(form, "ErrorPass", "")
                form = self.EditForm(form, "ErrorVerify", "")
                form = self.EditForm(form, "Pass", self.Get('password'))
                form = self.EditForm(form, "Verify", self.Get('verify'))

        # Email
        form = self.EditForm(form, "Email", self.Get('email'))
        if not self.IsValidEmail():
            form = self.EditForm(form, "ErrorEmail", self.ERR_EMAIL)
            Valid= False
        else:
            form = self.EditForm(form, "ErrorEmail", "")

        self.WriteForm(form)
        

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(form)

class TestHandler(webapp2.RequestHandler):
    def post(self):
        #q = self.request.get("q")
        #self.response.write(q)
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(self.request)

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/testform', TestHandler),
                               ('/ROT13', ROT13Handler),
                               ('/Signup',SignupHandler)
                              ], debug=True)
