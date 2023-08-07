#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

"""
Sotano Pong server
"""

#import os
import socket
import time
import threading
import sys

# telnet 127.0.0.1 1234

HOST = "localhost"
PORT = 1234

class connectionThread (threading.Thread):
    def __init__(self, conn, addr):
        print(f"New thread with conn={conn} and addr={addr}")
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print (f"Starting {self}, conn={conn}, addr={addr}")
    
        #print_time(self.name, self.counter, 5)
        
        print(f"Thread {self} run, connected by {addr}")
        with self.conn:
            for i in range(5):
                print(f"Thread {self}, message #{i}")
                data = self.conn.recv(1024)
                if not data:
                    break
                self.conn.sendall(data)
        
        print(f"Thread {self} exiting")


###################################################

print("Welcome to the Sotano Pong server!")
print()

threads = set()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
    # Bind the socket
    # Increment the port if already used. This is handy for developing.
    bind_error = True
    while bind_error:
        try:
            s.bind((HOST, PORT))
            bind_error = False
        except OSError:
            PORT += 1
    print(f"Bind, port {PORT}")
    
    print("Listening...")
    s.listen()
    
    # We have a new connection.
    # Let's create a thread for it
    while True:
        print("Accepting...")
        conn, addr = s.accept()
        print("Accepted")
        
        print(f"I have {len(threads)} threads")
        
        thread = connectionThread(conn, addr)
        threads.add(thread)
        thread.start()
        
        # Remove dead threads
        remove_set = set()
        for th in threads:
            if not th.is_alive():
                remove_set.add(th)
        for th in remove_set:
            print(f"Thread {th} is not alive, removing...")
            threads.remove(th)
