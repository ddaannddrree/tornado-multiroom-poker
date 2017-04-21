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

    def add_roomnick(self, room, nick):
        """Add nick to room. Return generated clientID"""
        # meant to be called from the main handler (page where somebody indicates a nickname and a room to join)
        cid = uuid.uuid4().hex  # generate a client id.
        if not room in self.room_info:  # it's a new room
            self.room_info[room] = []
        c = 1
        nn = nick
        nir = self.nicks_in_room(room)
        while True:
            if nn in nir:
                nn = nick + str(c)
            else:
                break
            c += 1

        self.client_info[cid] = {'room': room, 'nick': nn}  # we still don't know the WS connection for this client
        self.room_info[room].append({'cid': cid, 'nick': nn})
        return cid

    def add_client_wsconn(self, client_id, conn):
        """Store the websocket connection corresponding to an existing client."""
        self.client_info[client_id]['wsconn'] = conn
        cid_room = self.client_info[client_id]['room']

        if cid_room in self.roomates:
            self.roomates[cid_room].add(conn)
        else:
            self.roomates[cid_room] = {conn}

        for user in self.room_info[cid_room]:
            if user['cid'] == client_id:
                user['wsconn'] = conn
                break
        # send "join" and and "nick_list" messages
        self.send_join_msg(client_id)
        nick_list = self.nicks_in_room(cid_room)
        cwsconns = self.roomate_cwsconns(client_id)
        self.send_nicks_msg(cwsconns, nick_list)

    def remove_client(self, client_id):
        """Remove all client information from the room handler."""
        cid_room = self.client_info[client_id]['room']
        nick = self.client_info[client_id]['nick']
         # first, remove the client connection from the corresponding room in self.roomates
        client_conn = self.client_info[client_id]['wsconn']
        if client_conn in self.roomates[cid_room]:
            self.roomates[cid_room].remove(client_conn)
            if len(self.roomates[cid_room]) == 0:
                del(self.roomates[cid_room])
        r_cwsconns = self.roomate_cwsconns(client_id)
        # filter out the list of connections r_cwsconns to remove clientID
        r_cwsconns = [conn for conn in r_cwsconns if conn != self.client_info[client_id]['wsconn']]
        self.client_info[client_id] = None
        for user in self.room_info[cid_room]:
            if user['cid'] == client_id:
                self.room_info[cid_room].remove(user)
                break
        self.send_leave_msg(nick, r_cwsconns)
        nick_list = self.nicks_in_room(cid_room)
        self.send_nicks_msg(r_cwsconns, nick_list)
        if len(self.room_info[cid_room]) == 0:  # if room is empty, remove.
            del(self.room_info[cid_room])

    def nicks_in_room(self, rn):
        """Return a list with the nicknames of the users currently connected to the specified room."""
        nir = []  # nicks in room
        for user in self.room_info[rn]:
            nir.append(user['nick'])
        return nir

    def roomate_cwsconns(self, cid):
        """Return a list with the connections of the users currently connected to the room where
        the specified client (cid) is connected."""
        cid_room = self.client_info[cid]['room']
        r = []
        if cid_room in self.roomates:
            r = self.roomates[cid_room]
        return r




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
