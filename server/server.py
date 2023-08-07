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


class connectionThread(threading.Thread):
    """
    An established-connection thread
    """
    def __init__(self, conn, addr):
        print(f"New thread with conn={conn} and addr={addr}")
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print (f"Starting {self}, conn={self.conn}, addr={self.addr}")
    
        #print_time(self.name, self.counter, 5)
        
        print(f"Thread {self} run, connected by {self.addr}")
        with self.conn:
            for i in range(5):
                print(f"Thread {self}, message #{i}")
                data = self.conn.recv(1024)
                if not data:
                    break
                self.conn.sendall(data)
        
        print(f"Thread {self} exiting")

class ConnectionListenerThread(threading.Thread):
    """
    A thread to handle connections.
    It's useful to free the main thread from blocking.
    """
    def __init__(self, HOST, PORT):
        print("New ConnectionListenerThread")
        threading.Thread.__init__(self)
        
        self.threads = set()        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket
        # Increment the port if already used. This is handy for developing.
        bind_error = True
        while bind_error:
            try:
                self.s.bind((HOST, PORT))
                bind_error = False
            except OSError:
                PORT += 1
        print(f"Bind, port {PORT}")
    
    def get_num_threads(self):
        """
        Get the number of threads
        """
        return len(self.threads)


    def run(self):
        print (f"Starting ConnectionListenerThread")
        print("Listening...")
        self.s.listen()

        while True:
            print(f"CLT Accepting..., s={self.s}")
            conn, addr = self.s.accept()
            print("CLT Accepted")

            thread = connectionThread(conn, addr)
            self.threads.add(thread)
            thread.start()

    def cleanup(self):
        '''
        Remove dead threads
        '''
        remove_set = set()
        for th in self.threads:
            if not th.is_alive():
                remove_set.add(th)
        for th in remove_set:
            print(f"Thread {th} is not alive, removing...")
            self.threads.remove(th)

###################################################

print("Welcome to the Sotano Pong server!")
print()


HOST = "localhost"
PORT = 1234
    
listener_thread = ConnectionListenerThread(HOST, PORT)
listener_thread.start()

while True:
    print("Hi from the server, I'm awake")
    print(f"I have {listener_thread.get_num_threads()} threads")
    
    listener_thread.cleanup()
    
    print("I'm going to sleep")
    time.sleep(10)
