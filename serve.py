#!/usr/bin/env python3
"""Tiny local server. Framer's JS modules can't load from file://, so serve the folder over http."""
import http.server, socketserver, webbrowser, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.webp':'image/webp','.woff2':'font/woff2'}
with socketserver.TCPServer(("",8000),H) as s:
    print("Open http://localhost:8000  (Ctrl+C to stop)"); webbrowser.open("http://localhost:8000"); s.serve_forever()
