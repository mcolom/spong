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
Sotano Pong commands
"""

from enum import Enum
SPongCommands = Enum('command', ['PING', 'PONG', 'PLAYER_RENAME', 'BAD_FORMAT', 'CONN_REFUSED', 'GAME_START', 'GAME_OVER', 'PLAYERS_UPDATE', 'GET_PLAYERS_QUEUE', 'WHOS_PLAYING', 'BALLS_UPDATE', 'HIT_NOTIFICATION', 'DEBUG_TEXT_MESSAGE'])
