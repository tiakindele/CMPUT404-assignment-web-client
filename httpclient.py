#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

"""
Copyright 2019 Toluwanimi Akindele

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        print ("BODY:\n{}".format(self.body))

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        http_status_code = data[:data.find("\n")]
        return int(http_status_code.split()[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8', errors='ignore')

    def GET(self, url, args=None):
        urlP = urllib.parse.urlparse(url)
        hostname = urlP.hostname
        portval = urlP.port
        path = urlP.path

        if portval == None:
            portval = 80
        self.connect(hostname, portval)

        # prepare and send data
        path = "/" if path == "" else path
        data = "GET "+path+" HTTP/1.1\r\nHost: "+hostname+"\r\nConnection: close\r\n\r\n"
        self.sendall(data)
        
        # receive response
        response = self.recvall(self.socket)

        # extract and set code
        code = self.get_code(response)

        # extract and set body
        body = self.get_body(response)
        
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        urlP = urllib.parse.urlparse(url)
        hostname = urlP.hostname
        portval = urlP.port
        path = "/" if urlP.path == "" else urlP.path
        content = "" if args is None else urllib.parse.urlencode(args)
        content_len = str(0 if args is None else len(content))

        # prepare data to send
        data = "POST " + path + " HTTP/1.1\r\n"
        if portval is None:
            data += "Host: "+hostname+"\r\nAccept: */*\r\nConnection: close\r\n"
        else:
            data += "Host: "+hostname+":"+str(portval)+"\r\nAccept: */*\r\nConnection: close\r\n"
        data += "Content-Type: application/x-www-form-urlencoded\r\n"
        data += "Content-Length: "+content_len+"\r\n\r\n"+content
        
        # connect and send
        self.connect(hostname, portval)
        self.sendall(data)

        # receive response
        response = self.recvall(self.socket)

        # extract and set code
        code = self.get_code(response)

        # extract and set body
        body = self.get_body(response)
        
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))