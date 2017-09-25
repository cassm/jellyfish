#!/usr/bin/env python

from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import time
import math
import random
import socket
import fcntl
import struct
import errno
import optparse
import itertools
from operator import add
try:
    import json
except ImportError:
    import simplejson as json

import opc
import color_utils

##############################

import getopt
import textwrap
import sys
from ola import OlaClient
import select

import threading

##############################

import colours
import pattern_utils

import spiral
import sparkle
import wash

import rainbow_waves
import wobbler

import palettes

##############################

n_pixels_per_string = 50
n_strings = 8
n_pixels = n_strings * n_pixels_per_string

fps = 60

last_measured_time = time.time()
effective_time = time.time()

pixels = [(0.0, 0.0, 0.0) for i in range(n_pixels)]

speed_val = 1
mode_id = 5
last_mode_id = 0
audio_level = 0.5
audio_respond = False
auto_colour = False
colour_mash = False
mode_cycle = False

def process_dmx_frame(data):
    global speed_val
    global mode_id
    global audio_level
    global audio_respond
    global auto_colour
    global colour_mash
    global mode_cycle

    if len(data) != 7:
        return

    speed_val = data[0]/32.0
    mode_id = data[1]
    audio_level = data[2] / 255.0
    audio_respond = data[3]
    auto_colour = data[4]
    colour_mash = data[5]
    mode_cycle = data[6]


def main():
    global pixels
    global last_measured_time
    global effective_time
    global last_mode_id

    # initialise DMX slave listener
    ola_client = OlaClient.OlaClient()
    sock = ola_client.GetSocket()
    ola_client.RegisterUniverse(1, ola_client.REGISTER, process_dmx_frame)

    # handle command line
    parser = optparse.OptionParser()
    parser.add_option('-l', '--layout', dest='layout', default='layouts/disc-' + str(n_strings) + '.json',
                      action='store', type='string',
                      help='layout file')
    parser.add_option('-s', '--server', dest='server', default='127.0.0.1:7890',
                      action='store', type='string',
                      help='ip and port of server')

    options, args = parser.parse_args()

    # parse layout file
    print '\n\tparsing layout file\n'

    coordinates = []
    for item in json.load(open(options.layout)):
        if 'point' in item:
            coordinates.append(tuple(item['point']))

    # connect to openpixelcontrol server
    client = opc.Client(options.server)
    if client.can_connect():
        print('    connected to %s' % options.server)
    else:
        # can't connect, but keep running in case the server appears later
        print('    WARNING: could not connect to %s' % options.server)
    print('')

    sparkle.init(n_pixels)

    # send pixels
    print('\tsending pixels forever (control-c to exit)...\n')

    while True:
        # audio_level = math.sin(effective_time*6) / 2 + 0.5

        frame_start = time.time()

        if last_mode_id != mode_id:
            print "Mode switch {} -> {}".format(last_mode_id, mode_id)
            last_mode_id = mode_id
        # check for new dmx frames
        readable, writable, exceptional = select.select([sock], [], [], 0)
        while readable:
            ola_client.SocketReady()
            readable, writable, exceptional = select.select([sock], [], [], 0)

        # update effective time in line with speed value
        effective_time += (time.time() - last_measured_time) * speed_val
        last_measured_time = time.time()

        if mode_id == 0:
            wash.set_pixels(pixels, n_pixels_per_string, effective_time, palettes.auto, audio_level, audio_respond)

        elif mode_id == 1:
            sparkle.set_pixels(pixels, n_pixels_per_string, 0.5, 5, effective_time, palettes.auto, audio_level, audio_respond)

        elif mode_id == 2:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, True, effective_time, palettes.auto, audio_level, audio_respond)

        elif mode_id == 3:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, False, effective_time, palettes.auto, audio_level, audio_respond)

        elif mode_id == 4:
            rainbow_waves.set_pixels(pixels, effective_time, 29, -13, 19, audio_level, audio_respond)

        elif mode_id == 5:
            wobbler.set_pixels(pixels, n_pixels_per_string, effective_time, audio_level, audio_respond)

        client.put_pixels(pixels, channel=0)

        frame_duration = time.time() - frame_start
        frame_delay = 1.0 / fps

        if frame_delay > frame_duration:
          time.sleep(frame_delay - frame_duration)

if __name__ == "__main__":
    main()
