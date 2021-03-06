import socket

class WWW:
  
  def __init__(self,port=80,fdir='htm'):
    self.fdir = fdir
    self.port = port
    self.sock = socket.socket()
    self.count = 0
    
  def head(self,path=''):
    ctype = "text/css"
    if path.find('.htm') > -1: ctype = "text/html"
    return b"HTTP/1.1 200 OK\r\nContent-Type:%s; charset=utf-8\r\nServer:microPython,\r\n\r\n" % (ctype)
    
  def page(self,req,res):
    if req['path'] == '/': 
      req['path'] = '/index.htm'
    with open(self.fdir+req['path'], 'rb') as html:
      chead = self.head(req['path']) 
      chunk =  chead + html.read(256-len(chead))
      while chunk:
        res.sendall(chunk) # OSError: [Errno 104] ECONNRESET
        chunk = html.read(256)
    
  def request(self,req,res):
    bits = req['get'].split(' ') 
    if len(bits) == 3:
      req['method'],req['path'],_ = bits   #['GET', '/', 'HTTP/1.1']
      self.page(req,res)

  def serve(self):
    ai = socket.getaddrinfo("0.0.0.0", self.port)
    addr = ai[0][-1]
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind(addr)
    self.sock.listen(5)

    while True:
      bits = self.sock.accept()
      self.count += 1
      print(self.count,bits)
      res = bits[0]
      req = {
        "addr": bits[1],
        "head": [],
        "path": None,
        "get": res.readline().decode('UTF-8').rstrip()
      }

      while True:
        h = res.readline()
        if h == b"" or h == b"\r\n":
          break
        else:
          req['head'].append(h.decode('UTF-8').rstrip())
      
      self.request(req,res)
      res.close()


'''
import wwwtest
wwwtest.WWW().serve()
'''
