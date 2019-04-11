#!/usr/bin/env python3.7
"""

"""

from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from socketserver import UnixStreamServer
from typing import List, Dict, Tuple, Union
from threading import Event
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Part:
	data: bytes = field(default=b'')
	event: Event = field(default_factory=Event)
	
	def wait(self) -> bytes:
		self.event.clear()
		self.event.wait()
		return self.data
	
	def set(self, data: bytes):
		self.data = data
		self.event.set()


@dataclass
class Client:
	parts: Dict[str, Part] = field(default_factory=lambda: defaultdict(Part))
	
	def __getitem__(self, name: str) -> Part:
		return self.parts[name]


_g_clients: Dict[str, Client] = defaultdict(Client)


class RequestHandler(SimpleHTTPRequestHandler):
	protocol_version = 'HTTP/1.1'

	def do_GET(self):
		if self.path == '/':
			self.directory = 'static'
			super().do_GET()
		elif self.path == '/favicon.ico':
			self.directory = 'static'
			super().do_GET()
		elif self.path.startswith('/static/'):
			self.path = self.path[len('/static'):]
			self.directory = 'static'
			super().do_GET()
		elif self.path.startswith('/c/'):
			self.do_GET_client()
		else:
			print('GET', self.path)
			raise NotImplementedError
	
	def do_GET_client(self):
		"""GET /c/{id}/{name}/ -[long poll]-> {data}"""
		_, c, id, name, _2 = self.path.split('/')
		
		if name == 'view':
			self.do_GET_view()
		elif name == 'control':
			self.do_GET_control()
		else:
			self.do_GET_part()
	
	def do_GET_view(self):
		"""GET /c/{id}/view/ -> {html}"""
		path = Path.cwd() / 'static' / 'view.html'
		content = path.read_bytes()
		self.send('text/html', content)
	
	def do_GET_control(self):
		"""GET /c/{id}/control/ -> {html}"""
		path = Path.cwd() / 'static' / 'control.html'
		content = path.read_bytes()
		self.send('text/html', content)
	
	def do_GET_part(self):
		"""GET /c/{id}/{name}/ -[long poll]-> {data}"""
		_, c, id, name, _2 = self.path.split('/')
		client = _g_clients[id]
		part = client[name]
		content = part.wait()
		self.send('text/plain', content)

	def do_POST(self):
		length = self.headers['content-length']
		nbytes = int(length)
		data = self.rfile.read(nbytes)
		# throw away extra data? see Lib/http/server.py:1203-1205
		self.data = data
		
		if self.path.startswith('/c/'):
			self.do_POST_client()
		else:
			print('POST', self.path)
			raise NotImplementedError
	
	def do_POST_client(self):
		"""POST /c/{id}/{part}/ {data} -> ok"""
		_, c, id, name, _2 = self.path.split('/')
		
		client = _g_clients[id]
		part = client[name]
		part.set(self.data)
		
		self.send('text/plain', b'ok')

	def send(self, content_type, content):
		use_keep_alive = self._should_use_keep_alive()
		use_gzip = self._should_use_gzip()

		if use_gzip:
			import gzip
			content = gzip.compress(content)
		
		self.send_response(200)
		self.send_header('Content-Type', content_type)
		self.send_header('Content-Length', str(len(content)))
		if use_keep_alive:
			self.send_header('Connection', 'keep-alive')
		if use_gzip:
			self.send_header('Content-Encoding', 'gzip')
		self.end_headers()
		self.wfile.write(content)

	def _should_use_keep_alive(self):
		connection = self.headers['connection']
		if connection is None:
			return False
		if connection != 'keep-alive':
			return False
		return True
	
	def _should_use_gzip(self):
		accept_encoding = self.headers['accept-encoding']
		if accept_encoding is None:
			return False
		if 'gzip' not in accept_encoding:
			return False
		return True


class UnixRequestHandler(RequestHandler):
	def address_string(self):
		forwarded = self.headers['forwarded']
		d = {}
		for item in forwarded.split(';'):
			k, v = item.split('=')
			d[k] = v
		return d['for']


class ThreadingUnixHTTPServer(ThreadingHTTPServer, UnixStreamServer):
	def server_bind(self):
		address = self.server_address
		path = Path(address)
		if path.exists():
			path.unlink()
		super().server_bind()
		path.chmod(0o666)


def main(bind, port):
	address = (bind, port)
	print(f'Listening on {address}')
	server = ThreadingHTTPServer(address, RequestHandler)
	server.serve_forever()


def main(address, server_class, handler_class):
	print(f'Listening on {address}')
	server = server_class(address, handler_class)
	server.serve_forever()


def main_unix(bind):
	address = bind
	server_class = ThreadingUnixHTTPServer
	handler_class = UnixRequestHandler
	main(address, server_class, handler_class)


def main_tcp(bind, port):
	address = (bind, port)
	server_class = ThreadingHTTPServer
	handler_class = RequestHandler
	main(address, server_class, handler_class)


def cli():
	import argparse

	parser = argparse.ArgumentParser()
	parser.set_defaults(main=None)
	subparsers = parser.add_subparsers(required=True, dest='cmd')
	
	unix = subparsers.add_parser('unix')
	unix.set_defaults(main=main_unix)
	unix.add_argument('--bind', required=True)
	
	tcp = subparsers.add_parser('tcp')
	tcp.set_defaults(main=main_tcp)
	tcp.add_argument('--bind', default='0.0.0.0')
	tcp.add_argument('--port', type=int, default=8800)
	
	args = vars(parser.parse_args())
	args.pop('cmd')
	main = args.pop('main')

	main(**args)


if __name__ == '__main__':
	cli()
