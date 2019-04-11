#!/usr/bin/env python3.7
"""

"""

from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from socketserver import UnixStreamServer
from typing import List, Dict, Tuple, Union
from threading import Event
from pathlib import Path


_g_peer: bytes = b''
_g_recenter = Event()
_g_size: bytes = b'1'
_g_size_event = Event()


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
			super().do_GET()
		elif self.path == '/peer/':
			self.do_GET_peer()
		elif self.path == '/recenter/':
			self.do_GET_recenter()
		elif self.path == '/size/':
			self.do_GET_size()
		else:
			print('GET', self.path)
			raise NotImplementedError
	
	def do_GET_peer(self):
		"""GET /peer/ -> id"""
		
		content = _g_peer
		self.send('text/plain', content)
	
	def do_GET_recenter(self):
		"""GET /recenter/ -[long poll]-> ok"""
		
		_g_recenter.clear()
		_g_recenter.wait()
		self.send('text/plain', b'ok')
	
	def do_GET_size(self):
		"""GET /size/ -[long poll]-> {size}"""
		_g_size_event.clear()
		_g_size_event.wait()
		self.send('text/plain', _g_size)
	
	def do_POST(self):
		length = self.headers['content-length']
		nbytes = int(length)
		data = self.rfile.read(nbytes)
		# throw away extra data? see Lib/http/server.py:1203-1205
		self.data = data

		if self.path == '/peer/':
			self.do_POST_peer()
		elif self.path == '/recenter/':
			self.do_POST_recenter()
		elif self.path == '/size/':
			self.do_POST_size()
		else:
			print('POST', self.path)
			raise NotImplementedError
	
	def do_POST_peer(self):
		global _g_peer
		_g_peer = self.data
		
		self.send('text/plain', b'ok')
	
	def do_POST_recenter(self):
		_g_recenter.set()
		self.send('text/plain', b'ok')
	
	def do_POST_size(self):
		global _g_size
		_g_size = self.data
		_g_size_event.set()
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
