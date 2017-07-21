from google.appengine.ext import ndb

class Bmail(ndb.Model):
    recipient = ndb.StringProperty()
    subject = ndb.StringProperty()
    text = ndb.StringProperty()
    sender = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)