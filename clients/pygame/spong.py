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
import sys

import pygame
from pygame.locals import *

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
    
# Send a ping
msg = bytes((67, 1, 0xAB))
conn.send(msg)

# Receive the answer
ans = conn.recv(1024)
print(ans)

# Change our name
name = "tibur"
msg = b"C" + bytes((2,)) + bytes(name, encoding="utf8") + bytes((0, ))
conn.send(msg)

ans = conn.recv(1024)
print(ans)





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
