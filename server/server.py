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
import random
import socket
import select
import time
import threading
import sys

# telnet 127.0.0.1 1234


class connectionThread(threading.Thread):
    """
    An established-connection thread
    """
    def __init__(self, conn, addr, on_data_available_handler=None):
        #print(f"New thread with conn={conn}, addr={addr}, on_data_available_handler={on_data_available_handler}")
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.on_data_available_handler = on_data_available_handler
        self.socket_is_connected = True

    def run(self):
        """
        Thread loop, until the connection is closed.
        It blocks until data is available and notifies with an event.
        """
        #print (f"Starting {self}, conn={self.conn}, addr={self.addr}, on_data_available_handler={self.on_data_available_handler}")
        #print(f"Thread {self} run, connected by {self.addr}")
        
        while self.socket_is_connected:
            try:
                # We use select to avoid that the thread get blocked in
                # recv when we ask to finish.
                readable, _, _ = select.select((self.conn,), (), (), 1)
                if readable:
                    data = self.conn.recv(1024)
                    if not data:
                        self.socket_is_connected = False
                        break                
                    # Fire notification event
                    if self.on_data_available_handler:
                        self.on_data_available_handler(data)
            except OSError:
                self.socket_is_connected = False
                
    def send_data(self, data):
        """
        Send data
        """
        try:
            self.conn.sendall(data)
        except OSError:
            self.socket_is_connected = False
    
    def is_connected(self):
        """
        Check if the socked is still connected
        """
        return self.socket_is_connected
        
    def close_connection(self):
        """
        Close the connection
        """
        self.conn.close()
        self.socket_is_connected = False

        

class ConnectionListenerThread(threading.Thread):
    """
    A thread to handle connections.
    It's useful to free the main thread from blocking.
    It'll fire an event when a new connection is established.
    """
    def __init__(self, HOST, PORT, new_connection_handler=None):
        print("New ConnectionListenerThread")
        threading.Thread.__init__(self)
        
        self.threads = set()        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_handler = new_connection_handler
        self.must_finish = False
        self.conn = None

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
        #print(f"Starting ConnectionListenerThread")
        self.s.listen()
        
        while not self.must_finish:
            # We use select to avoid that the thread can't be finished
            readable, _, _ = select.select((self.s,), (), (), 1)
            if self.s in readable:
                self.conn, addr = self.s.accept()
                print(f"CLT Accepted: conn={self.conn}")

                thread = connectionThread(self.conn, addr)
                self.threads.add(thread)
                
                # Fire the new_connection_handler event
                if self.new_connection_handler:
                    self.new_connection_handler(thread)
        
        print("CLT closing all")
        self.cleanup()
        if self.conn:
            self.conn.close()
    
    def finish(self):
        """
        Notify the thread that it needs to finish
        """
        if self.conn:
            self.conn.close()
        print("FINISH")
        self.must_finish = True

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
            th.close_connection()
            th.join()
            self.threads.remove(th)


class Player():
    """
    A player.
    """
    def __init__(self, name, thread):
        print(f"New Player, name = {name}, thread={thread}")
        self.name = name
        self.thread = thread
        
        self.thread.on_data_available_handler = self.data_received
        self.thread.start()
    
    def data_received(self, data):
        print(f"Player data_received: {data}")
        
        # Is it a command (it begins with byte 'C')
        if data[0] == ord(b'C'):
            print("It's command")
            command = data[1]
            if command == 1: # Ping
                print("Ping")
                num = data[2]
                self.thread.send_data((bytes((num+1,))))
                
        else:
            # Echo
            self.thread.send_data(data)
        
        # Close the connection with control-C in telnet.
        # This is just for debugging, and not at all a clean closing!
        if data == b'\xff\xfb\x06':
            print(f"reee: {self.thread.conn}")
            self.thread.conn.close()


###################################################

def new_connection_handler(thread):
    print("new_connection_handler")
    
    # Create a player and give its newly created communication thread.
    # The thread is started by the player, not here.
    player = Player("Player" + str(int(100*random. random())), thread)


print("Welcome to the Sotano Pong server!")
print()


HOST = "localhost"
PORT = 1234
    
listener_thread = ConnectionListenerThread(HOST, PORT, new_connection_handler=new_connection_handler)
listener_thread.start()

try:
    while True:
        listener_thread.cleanup()
        print(f"I have {listener_thread.get_num_threads()} threads")
        time.sleep(10)
except KeyboardInterrupt:
    listener_thread.finish()

#listener_thread.join()
