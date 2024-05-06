from gevent import monkey
monkey.patch_all()
import json
from flask import Flask, render_template
from flask_sockets import Sockets
import json
from terminal import Terminal,TerminalManager
import logging 
from gevent import pywsgi
import argparse
from geventwebsocket.handler import WebSocketHandler

flask_app = Flask(__name__,static_folder = "./dist/static", template_folder = "./dist")
sockets = Sockets(flask_app)

logging.basicConfig(level=logging.INFO,format='[%(asctime)s] - %(levelname)s - %(message)s')



@sockets.route('/term')
def echo_socket(ws):

    term = TerminalManager(ws)
    id = term.create(autoclose=True,log=logging)
    obj = term.terminals[id]
    while not ws.closed:
        message = ws.receive()
        if message is None:
            term.kill(id)
        else:
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

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Access system terminal in web browser."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default="0.0.0.0", help="host address to run server on ")
    parser.add_argument("--port", default=8000, help="port to run server on")

    args = parser.parse_args()
    server = pywsgi.WSGIServer((args.host, int(args.port)), flask_app, handler_class=WebSocketHandler)
    logging.info("Terminal Started on http://%s:%s",args.host,args.port)
    server.serve_forever()

if __name__ == "__main__":
    main()
    
