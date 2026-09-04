import argparse, json, mimetypes
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .storage import Storage

STORAGE=Storage(Path("shared"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/files": return self.send_json(200,STORAGE.list())
        if path.startswith("/files/"):
            try: data=STORAGE.read(path[7:])
            except (ValueError,FileNotFoundError): return self.send_json(404,{"error":"file not found"})
            self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(path)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        self.send_json(404,{"error":"route not found"})
    def do_PUT(self):
        path=urlparse(self.path).path
        if not path.startswith("/files/"): return self.send_json(404,{"error":"route not found"})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>STORAGE.max_bytes: raise ValueError("file is too large")
            result=STORAGE.save(path[7:],self.rfile.read(length)); self.send_json(201,result)
        except (ValueError,FileExistsError) as exc: self.send_json(400,{"error":str(exc)})
    def send_json(self,status,payload):
        body=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self,format,*args): return

def main(argv=None):
    global STORAGE
    parser=argparse.ArgumentParser(description="Share files on a trusted local network"); parser.add_argument("--folder",type=Path,default=Path("shared")); parser.add_argument("--host",default="127.0.0.1"); parser.add_argument("--port",type=int,default=8080); args=parser.parse_args(argv)
    STORAGE=Storage(args.folder); server=ThreadingHTTPServer((args.host,args.port),Handler); print(f"LAN Drop: http://{args.host}:{args.port}/files")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nStopping server")
    finally: server.server_close()

if __name__=="__main__": main()

