#!/usr/bin/env python
import os
import jinja2
import webapp2
import cgi
import json

from google.appengine.api import users
from google.appengine.api import urlfetch
from models import Bmail

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            sign_in = True
            logout_url = users.create_logout_url("/")
            params = {
                "user": user,
                "sign_in": sign_in,
                "logout_url": logout_url,
            }
            return self.render_template("hello.html", params)
        else:
            sign_in = False
            login_url = users.create_login_url("/")
            params = {
                "user": user,
                "sign_in": sign_in,
                "login_url": login_url,
            }
            return self.render_template("bmail.html", params)

class NewMessageHandler(BaseHandler):
    def get(self):
        logout_url = users.create_logout_url("/")
        params = {
            "logout_url": logout_url
        }
        return self.render_template("new-message.html", params)

class SaveHandler(BaseHandler):
    def post(self):
        to = cgi.escape(self.request.get("to"))
        subject = cgi.escape(self.request.get("subject"))
        message = cgi.escape(self.request.get("text"))

        user = users.get_current_user()
        if user:
            sender = user.email()

        save = Bmail(recipient=to, subject=subject, text=message, sender=sender)
        save.put()

        return self.render_template("save.html")

class SentMessagesHandler(BaseHandler):
    def get(self):
        logout_url = users.create_logout_url("/")
        user = users.get_current_user()
        if user:
            email = user.email()
            all_messages = Bmail.query(Bmail.sender == email).fetch()
            params = {
                "all_messages": all_messages,
                "logout_url": logout_url
            }

            return self.render_template("all_messages.html", params)

class InboxHandler(BaseHandler):
    def get(self):
        logout_url = users.create_logout_url("/")
        user = users.get_current_user()
        if user:
            email = user.email()
            inbox = Bmail.query(Bmail.recipient == email).fetch()
            params = {
                "inbox": inbox,
                "logout_url": logout_url
            }

            return self.render_template("inbox.html", params)

class WeatherHandler(BaseHandler):
    def get(self):
        url = "https://opendata.si/vreme/report/?lat=47.05&lon=12.92"

        data = urlfetch.fetch(url).content

        json_data = json.loads(data)

        weather = json_data["forecast"]["data"][0]["rain"]
        weather_clouds = json_data["forecast"]["data"][0]["clouds"]

        params = {
            "weather": weather,
            "weather_clouds": weather_clouds
        }

        return self.render_template("weather.html", params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/new-message', NewMessageHandler),
    webapp2.Route('/save', SaveHandler),
    webapp2.Route('/sent-messages', SentMessagesHandler),
    webapp2.Route('/inbox', InboxHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)
