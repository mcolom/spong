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
Sotano Pong PyGame client
"""

# PyGame tutorial: https://coderslegacy.com/python/python-pygame-tutorial/

import socket
import time
import random
import os
import threading
import sys

import pygame
from pygame.locals import *

# Import the command definitions
# We've put them in a separate file.
# The same files is shared by both server and clients
ROOT = os.path.abspath(os.curdir)
commands_py_dir = os.path.abspath(os.path.join(ROOT, "../../"))
sys.path.append(commands_py_dir)
from commands import SPongCommands


# Screen size
# See https://www.msx.org/wiki/Screen_Modes_Description for MSX modes
SCALE = 7

SCREEN_WIDTH = 256 * SCALE
SCREEN_HEIGHT = 212 * SCALE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Ball(pygame.sprite.Sprite):
    """
    The ball
    """
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/ball.png")
        self.rect = self.image.get_rect()
        self.rect.center=(random.randint(40,SCREEN_WIDTH-40),0)

    def move(self):
        """
        Move the ball
        """
        self.rect.move_ip(1 * SCALE, 3 * SCALE)
        if (self.rect.bottom > SCREEN_HEIGHT):
            self.rect.top = 0
            self.rect.center = (random.randint(100, 100), 0)

    def draw(self, surface):
        """
        Draw the ball
        """
        surface.blit(self.image, self.rect) 


class Paddle(pygame.sprite.Sprite):
    """
    A generic-class Pong paddle
    """
    def __init__(self):
        super().__init__() 
        self.x = 0
        self.y = 0

    def draw(self, surface):
        """
        Draw the paddle
        """
        surface.blit(self.image, self.rect) 

class PaddleUp(Paddle):
    """
    The UP paddle
    """
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/paddle_up.png")
        self.rect = self.image.get_rect()
        self.rect.center = (0, 50)
    
    def move(self):
        self.rect.move_ip(self.x + 1*SCALE, 0)
        if (self.rect.left > SCREEN_WIDTH):
            self.rect.left = 0

class PaddleDown(Paddle):
    """
    The DOWN paddle
    """
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/paddle_down.png")
        self.rect = self.image.get_rect()
        self.rect.center = (250, SCREEN_HEIGHT - 50)
    
    def move(self):
        self.rect.move_ip(self.x + 1*SCALE, 0)
        if (self.rect.left > SCREEN_WIDTH):
            self.rect.left = 0

class PaddleRight(Paddle):
    """
    The RIGHT paddle
    """
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/paddle_right.png")
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 50, SCREEN_WIDTH - 50)
    
    def move(self):
        self.rect.move_ip(0, self.x + 1*SCALE)
        if (self.rect.top > SCREEN_WIDTH):
            self.rect.top = 0

class PaddleLeft(Paddle):
    """
    The LEFT paddle
    """
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("assets/paddle_left.png")
        self.rect = self.image.get_rect()
        self.rect.center = (50, 200)
    
    def move(self):
        self.rect.move_ip(0, self.x + 1*SCALE)
        if (self.rect.top > SCREEN_WIDTH):
            self.rect.top = 0
            

def connect_to_server(SERVER, PORT):
    """
    Connect to the server
    """
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connected = False
    for _ in range(10):
        try:
            conn.connect((SERVER, PORT))
            connected = True
            break
        except ConnectionRefusedError:
            PORT += 1
    
    if not connected:
        raise ConnectionRefusedError
    return conn, PORT


class connectionThread(threading.Thread):
    """
    An established-connection thread
    """
    def __init__(self, conn, on_data_available_handler=None):
        #print(f"New thread with conn={conn}, addr={addr}, on_data_available_handler={on_data_available_handler}")
        threading.Thread.__init__(self)
        self.conn = conn
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


##############################################

SERVER = "localhost"
PORT = 1234

print("Sótano Pong PyGame client")
print()

name = f"Player_{int(100*random. random())}"

# Connect to the server
try:
    conn, PORT = connect_to_server(SERVER, PORT)
except ConnectionRefusedError:
    print(f"Couldn't connect to the server {SERVER}!")
    sys.exit(0)

print(f"Connected to the server {SERVER}:{PORT}")

# Create the execution thread



    
# Send a ping
data = b"C" + bytes((SPongCommands.PING.value, )) +b'\xAB'
conn.send(data)

# Change our name
name = "tibur"
data = b"C" + bytes((SPongCommands.PLAYER_RENAME.value,)) + bytes(name, encoding="utf8") + b'\x00'
conn.send(data)

# Send a free text message to the server
data = b"C" + bytes((SPongCommands.DEBUG_TEXT_MESSAGE.value, )) + b"Hi from client " + b"'" + bytes(name, encoding="utf8") + b"'" + b'\x00'
conn.send(data)

# To be removed: this is just to confirm we receive an answer from the server!
try:
    ans = conn.recv(1024)
    while ans != b'': # loop until connection closed
        print(f"Answer: {ans}")
        # Receive more answers
        ans = conn.recv(1024)
except ConnectionResetError:
    pass

sys.exit(0)

FPS = 60
FramePerSec = pygame.time.Clock()

# Display initialization
pygame.init()
pygame.display.set_caption('Sótano Pong')
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# The sprites
ball = Ball()
paddle_up = PaddleUp()
paddle_right = PaddleRight()
paddle_down = PaddleDown()
paddle_left = PaddleLeft()

# Main loop
do_exit = False

while not do_exit:
    ball.update()
    ball.move()

    paddle_up.update()
    paddle_up.move()
    #
    paddle_right.update()
    paddle_right.move()
    #
    paddle_down.update()
    paddle_down.move()
    #
    paddle_left.update()
    paddle_left.move()
    
    DISPLAYSURF.fill(BLACK)
    
    ball.draw(DISPLAYSURF)

    paddle_up.draw(DISPLAYSURF)
    paddle_right.draw(DISPLAYSURF)
    paddle_down.draw(DISPLAYSURF)
    paddle_left.draw(DISPLAYSURF)

    pygame.display.update()
    FramePerSec.tick(FPS)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            do_exit = True

pygame.quit()
print("Bye!")
