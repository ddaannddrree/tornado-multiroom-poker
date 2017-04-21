import os
import uuid
import json
import tornado.ioloop
import tornado.web
from tornado import websocket


class RoomHandler(object):
    """Store data about connections, rooms, which users are in which rooms, etc."""
    def __init__(self):
        self.client_info = {}  # for each client id we'll store  {'wsconn': wsconn, 'room':room, 'nick':nick}
        self.room_info = {}  # dict  to store a list of  {'cid':cid, 'nick':nick , 'wsconn': wsconn} for each room
        self.roomates = {}  # store a set for each room, each contains the connections of the clients in the room.


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, room_handler):
        """Store a reference to the "external" RoomHandler instance"""
        self.__rh = room_handler

    def get(self):
        """Render chat.html if required arguments are present, render main.html otherwise."""
        try:
            room = self.get_argument("room")
            nick = self.get_argument("nick")
            cid = self.__rh.add_roomnick(room, nick)
            self.render("templates/chat.html", clientid=cid)
        except tornado.web.MissingArgumentError:
            self.render("templates/main.html")


if __name__ == "__main__":
    rh = RoomHandler()
    app = tornado.web.Application([
        (r"/", MainHandler, {'room_handler': rh})],
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

