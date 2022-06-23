# gevent - чтобы сделать Flask асинхронным
from gevent import monkey
monkey.patch_all()  # заменяет все I/O-операции на асинхронные

from gevent.pywsgi import WSGIServer
from app import app


http_server = WSGIServer(('', 5001), app)
http_server.serve_forever()