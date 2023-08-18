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

# telnet 127.0.0.1 1234

import os
import random
import socket
import select
import time
import threading
import sys

# Import the command definitions
# We've put them in a separate file.
# The same files is shared by both server and clients
ROOT = os.path.abspath(os.curdir)
commands_py_dir = os.path.abspath(os.path.join(ROOT, ".."))
sys.path.append(commands_py_dir)
from commands import SPongCommands


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
        self.must_finish = False

    def finish(self):
        """
        Notify the thread that it needs to finish
        """
        if self.conn:
            self.conn.close()
        print("FINISH connectionThread")
        self.must_finish = True

    def run(self):
        """
        Thread loop, until the connection is closed or asked to finish.
        It blocks until new data is available to read and notifies with an event.
        """
        #print (f"Starting {self}, conn={self.conn}, addr={self.addr}, on_data_available_handler={self.on_data_available_handler}")
        #print(f"Thread {self} run, connected by {self.addr}")
        
        while not self.must_finish and self.socket_is_connected:
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
            print(f"Server sending: {data}")
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
    def __init__(self, HOST, PORT, players, new_connection_handler=None):
        print("New ConnectionListenerThread")
        threading.Thread.__init__(self)
        
        self.threads = set()        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_handler = new_connection_handler
        self.must_finish = False
        self.players = players
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
                print(f"CLT accepted: conn={self.conn}")

                thread = connectionThread(self.conn, addr)
                self.threads.add(thread)
                
                # Fire the new_connection_handler event
                if self.new_connection_handler:
                    self.new_connection_handler(thread, self.players)
        
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
        print("CLT finish")
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
    
    def is_connected(self):
        """
        Check if the player is connected
        """
        return self.thread.is_connected()
    
    def finish(self):
        """
        Ask the player to finish
        """
        # Finish its thread
        if self.thread:
            self.thread.finish()
    
    def get_name(self):
        """
        Name getter
        """
        return self.name
    
    def process_ping(self, num):
        """
        Process ping
        """
        # Send a pong to the client
        data = b"C" + bytes((SPongCommands.PONG.value, )) + bytes((num, ))
        self.thread.send_data(data)
    
    def process_change_name(self, data):
        """
        Change player's name
        """
        if data[-1] != 0:
            self.thread.send_data((bytes((SPongCommands.BAD_FORMAT.value, )))) # Error
            return

        name = data[2:-1].decode()
        print(f"Player '{self.name}' changed its name to '{name}'")
        self.name = name

    def process_debug_text_message(self, data):
        """
        Process a debug text message received from the client
        """
        if data[-1] != 0:
            self.thread.send_data((bytes((SPongCommands.BAD_FORMAT.value, )))) # Error
            return

        text = data[2:-1].decode()
        print(f"Message from player '{self.name}': '{text}'")

    def text_debug_message_to_client(self, text):
        """
        Send a text message to the client
        """
        data = b"C" + bytes((SPongCommands.DEBUG_TEXT_MESSAGE.value, )) + bytes(text, encoding="utf8") + b'\x00'
        self.thread.send_data(data)
        
    def data_received(self, data):
        print(f"Player data_received: {data}")
        
        # Is it a command (it begins with byte 'C')
        if data[0] == ord(b'C'):
            command = data[1]
            if command == SPongCommands.PING.value:
                print("Ping")
                num = data[2]
                self.process_ping(num)
            elif command == SPongCommands.PONG.value:
                print("Pong from client")
                pass
            elif command == SPongCommands.PLAYER_RENAME.value:
                print("Change player's name")
                self.process_change_name(data)
            elif command == SPongCommands.DEBUG_TEXT_MESSAGE.value:
                print("Text message")
                self.process_debug_text_message(data)
            else:
                raise NotImplementedError(f"Command not implement: {command}")
        
        # Close the connection with control-C in telnet.
        # This is just for debugging, and not at all a clean closing!
        if data == b'\xff\xfb\x06':
            self.thread.conn.close()


###################################################

g_lock = threading.Lock()

# Players' queue
players = []

def add_new_player(name, thread, players):
    """
    Create and add new player
    """
    global g_lock
    
    player = Player("Player" + str(int(100*random. random())), thread)
    
    with g_lock:
        players.append(player)
    return player

def remove_player(player, players):
    """
    Finish and remove a player
    """
    global g_lock

    exists = player in players
    if exists:
        player.finish()
        with g_lock:
            players.remove(player)
    return exists

def cleanup(players):
    """
    Cleanup (disconnected players, etc.)
    """
    # Remove disconnected players
    all_players = players.copy()
    for player in all_players:
        if not player.is_connected():
            print(f"Cleanup removing disconnected player {player.get_name()}")
            remove_player(player, players)

def new_connection_handler(thread, players):
    print("new_connection_handler")
    
    # Create a player and give its newly created communication thread.
    # The thread is started by the player, not here.
    name = str(int(100*random. random()))
    player = add_new_player(name, thread, players)
    
    # Send a free text message to the client
    player.text_debug_message_to_client(f"Hi there, {player.name}!")


print("Welcome to the Sotano Pong server!")
print()


HOST = "localhost"
PORT = 1234
    
listener_thread = ConnectionListenerThread(HOST, PORT, players, new_connection_handler=new_connection_handler)
listener_thread.start()

i = 0

try:
    while True:
        listener_thread.cleanup()
        
        if i == 5:
            if len(players) > 0:
                player = players[0]
                print(f"Finishing player '{player.get_name()}'")
                #remove_player(player, players) # Let's leave cleanup(.) do this
                player.finish()
            i = 0
        
        cleanup(players)
        print(f"I have {listener_thread.get_num_threads()} threads, {len(players)} players")

        time.sleep(5)
        
        i += 1
except KeyboardInterrupt:
    listener_thread.finish()

#listener_thread.join()
