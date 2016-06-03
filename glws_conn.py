__author__ = 'nunosilva'

from socketIO_client import SocketIO, BaseNamespace

globalgetData = None
globalready = None


class fuck(BaseNamespace):

    def on_ready(self, *args):
        global globalready
        globalready = args[0]

    def on_getData(self, *args):
        global globalgetData
        globalgetData = args[0]

class makeSocket:

    def __init__(self):
        self.socket = SocketIO("https://glws.org/fuck")
        self.fn = self.socket.define(fuck, "/fuck")

    def emitready(self):
        try:
            self.fn.emit("isReady",{"wanna_fuck": "no thanks I\'m under age"})
            self.socket.wait(seconds=3)
            global globalready
            temp = globalready
            globalready = None
            return temp
        except TypeError:
            print 'something went wrong doing a ready command please try again'
            return False

    def emitgetdata(self, data):
        try:
            self.fn.emit("sendData", data)
            self.socket.wait(seconds=0.8)
            global globalgetData
            temp = globalgetData
            globalgetData = None
            return temp
        except TypeError:
            print 'something went wrong doing a sendData command please try again'
            return False