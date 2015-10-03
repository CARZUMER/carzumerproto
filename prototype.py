# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 03:08:50 2015

@author: Dan

This file contains the Prototype Project

"""

# Import section
# --------------
import web  # This is web.py -- central to the prototype
import cfg
from UserDBModule import UserDatabase
from WebIndex import IndexPost, IndexGet


def ListSort(L):
    return sorted(L)

#   SessionAll = (SessionConsumer, SessionFilterArray, SessionSelections)
class Index(object):
    def GET(self):
        (Consumer, FilterArray, Selections) = IndexGet()
        return render.CarZumerBrowse(Consumer, FilterArray, Selections)

    def POST(self):
        #global SessionConsumer, SessionFilterArray, SessionSelections
        #(SessionConsumer, SessionFilterArray, SessionSelections) = IndexPost()
        (Consumer, FilterArray, Selections) = IndexPost()
        return render.CarZumerBrowse(Consumer, FilterArray, Selections)


class count(object):
   def GET(self):
       return render.CarZumerCount()

UserDB = UserDatabase

# web.config.debug = False  # Addressing a known bug in Web.py

urls = (
        '/',        'Index',
        )

app = web.application(urls, globals())
application = app.wsgifunc()


render = web.template.render('templates/',
                             base="layout",
                             globals={'WebSort': ListSort})

if __name__ == "__main__":
    app.run()

