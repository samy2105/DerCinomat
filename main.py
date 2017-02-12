# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.ext import ndb


class Movie(ndb.Model):
    title_movie = ndb.StringProperty()
    regisseur = ndb.StringProperty()
    schauspieler = ndb.StringProperty()
    erscheinungsjahr = ndb.StringProperty()
    zusatzinfos = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
    gesehen = ndb.BooleanProperty(default=False)
    ansehen = ndb.BooleanProperty(default=False)


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
        movies = Movie.query(Movie.gesehen == True).fetch() #ladet die nachrichten, geloeschte werden nicht geladen

        listen = {"movies": movies}
        return self.render_template("base.html", params=listen)


class NewMovieHandler(BaseHandler):
    def get(self):
        return self.render_template("newmovie.html")

    def post(self):
        title = self.request.get("title")
        regisseur = self.request.get("regisseur")
        schauspieler = self.request.get("schauspieler")
        erscheinungsjahr = self.request.get("erscheinungsjahr")
        zusatzinfos = self.request.get("zusatzinfos")
        gesehen = self.request.get("gesehen")
        ansehen = self.request.get("ansehen")


        msg_object = Movie(title_movie=title, regisseur=regisseur, schauspieler=schauspieler, erscheinungsjahr=erscheinungsjahr, zusatzinfos=zusatzinfos) # Bezeichnungen in der Database
        if gesehen:
            msg_object.gesehen = True
        msg_object.put()

        return self.render_template("newmovie.html")

class OldMovieHandler(BaseHandler):
    def get(self):
        movies = Movie.query(Movie.gesehen == False or Movie.gesehen == None).fetch()
        listen = {"movies": movies}
        return self.render_template("movielist.html",params=listen)


class MessageEditHandler(BaseHandler):
    def get(self, message_id):
        movies = Movie.get_by_id(int(message_id))
        params = {"movies": movies}
        return self.render_template("message_edit.html", params=params)

    def post(self, message_id):
        new_title = self.request.get("movie_title")
        movies = Movie.get_by_id(int(message_id))
        movies.title = new_title
        movies.put()

        return self.redirect_to("base.html") #sorgt dafuer, dass auf diesselbe seite geladen wird

class MessageDeleteHandler(BaseHandler):
    def get(self, message_id):
        movies = Movie.get_by_id(int(message_id))

        listen = {"movies": movies}

        return self.render_template("message_delete.html", params=listen)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))

        message.deleted = True
        message.put()

        return self.redirect_to("base.html")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="uebersicht"),
    webapp2.Route('/newmovie', NewMovieHandler, name="newmovie"),
    webapp2.Route('/movielist', OldMovieHandler, name="movielist"),
    webapp2.Route('/message/<message_id:\d+>/edit', MessageEditHandler, name="message-edit"),
    webapp2.Route('/message/<message_id:\d+>/delete', MessageDeleteHandler, name="message-delete"),
], debug=True)
