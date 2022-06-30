# gevent - чтобы сделать Flask асинхронным
from gevent import monkey
monkey.patch_all()  # заменяет все I/O-операции на асинхронные

from gevent.pywsgi import WSGIServer
import sys, os
sys.path.append(os.path.dirname(__file__) + '/..')
# from auth_app import app
from auth_app import create_app

app = create_app()
http_server = WSGIServer(('', 5001), app)
http_server.serve_forever()
