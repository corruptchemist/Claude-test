# Threaded static host that mimics a real CDN: HTTP/1.1 keep-alive, gzip, HEAD.
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import gzip, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = open(os.path.join(ROOT, 'index.html'), 'rb').read()
GZ  = gzip.compress(RAW, 6)

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass
    def _serve(self, body):
        use_gz = 'gzip' in self.headers.get('Accept-Encoding', '')
        data = GZ if use_gz else RAW
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        if use_gz: self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        if body: self.wfile.write(data)
    def do_GET(self):  self._serve(True)
    def do_HEAD(self): self._serve(False)

print("raw=%d gzip=%d" % (len(RAW), len(GZ)), flush=True)
ThreadingHTTPServer(('127.0.0.1', 8099), H).serve_forever()
