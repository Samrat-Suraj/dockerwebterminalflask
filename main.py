import json
from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template
from werkzeug.debug import DebuggedApplication
from flask_sockets import Sockets
import binascii
import json
import os
from terminal import Terminal
import logging 
flask_app = Flask(__name__,static_folder = "./dist/static", template_folder = "./dist")
sockets = Sockets(flask_app)

logging.basicConfig(level=logging.INFO,format='[%(asctime)s] - %(levelname)s - %(message)s')

class TerminalManager(object):
    def __init__(self,ws=None):
        self.terminals = {}
        self.ws = ws

    def __getitem__(self, _id):
        return self.terminals[_id]

    def __contains__(self, _id):
        return _id in self.terminals

    def list(self):
        return [{
            'id': _id,
            'command': self[_id].command,
        } for _id in self.terminals.keys()]

    def create(self, **kwargs):
        _id = binascii.hexlify(os.urandom(32)).decode('utf-8')
        t = Terminal(self,id=_id,ws=self.ws,**kwargs)
        self.terminals[_id] = t
        return _id

    def kill(self, _id):
        self.terminals[_id].kill()
        self.remove(_id)

    def remove(self, _id):
        self.terminals.pop(_id)



@sockets.route('/term')
def echo_socket(ws):

    term = TerminalManager(ws)
    id = term.create(autoclose=True,log=logging)
    obj = term.terminals[id]

    while not ws.closed:
        message = ws.receive()
        data = json.loads(message)
        if 'resize' in data.keys():
            w = data['resize'][0]
            h = data['resize'][1]
            obj.resize(w,h)

        if 'data' in data.keys():
            obj.feed(data['data']) 

              

@flask_app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), flask_app, handler_class=WebSocketHandler)
    logging.info("Terminal Started on http://localhost:5000")
    server.serve_forever()
