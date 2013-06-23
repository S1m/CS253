#!/usr/bin/env python
#
# Created by: Simon Brunet 2013-06-19
#
# Abstract:
#   Store the DB models and DB related functions
#
###############################################################################

from google.appengine.ext import db

# Entry
#    Used for storing wiki entry
class Entry(db.Model):
    name = db.StringProperty(required = True)
    txt = db.TextProperty(required = True, indexed=False)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    
    def GetDict(self):
        s = {}
        s["name"] = self.name
        s["created"] = self.created.date().strftime("%B %d, %Y")
        s["last_modified"] = self.last_modified.date().strftime("%B %d, %Y")
        s["content"] = self.txt
        return s
    
# User
#    User for storing the User data
class User(db.Model):
    user = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

MODELS = {"Entry" : Entry,
          "User"  : User }

# Wrapper on Query to avoid explicit exposition of db model classes
class Query(db.Query):
    def __init__(self, model, **kwargs):
        super(Query, self).__init__(model_class = MODELS[model], **kwargs)
        
# Wrapper on Model to avoid explicit exposition of db model classes
def Model(model):
    return MODELS[model]
    
# Put an object to the DataStore
#   Ex: Put("Entry", title = title, txt = txt)
def Put(model, **kwargs):
    obj = MODELS[model](**kwargs)
    obj.put()
    # If needed, returns the object
    return obj


