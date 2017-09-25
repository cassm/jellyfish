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
import rainbow_waves
import spiral
import sparkle
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
mode_id = 0
last_mode_id = 0

def process_dmx_frame(data):
  global speed_val
  global mode_id
  speed_val = data[0]/64.0
  mode_id = data[1]

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
        frame_start = time.time()

        if last_mode_id != mode_id:
            print "Mode switch {} -> {}".format(last_mode_id, mode_id)
            last_mode_id = mode_id
        # check for new dmx frames
        readable, writable, exceptional = select.select([sock], [], [], 0)
        if readable:
            ola_client.SocketReady()

        # update effective time in line with speed value
        effective_time += (time.time() - last_measured_time) * speed_val
        last_measured_time = time.time()

        if mode_id == 0:
            sparkle.set_pixels(pixels, n_pixels_per_string, 0.5, 5, effective_time, palettes.auto)
        if mode_id == 1:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, effective_time, palettes.auto)
        elif mode_id == 2:
            rainbow_waves.set_pixels(pixels, effective_time, 29, -13, 19)
        elif mode_id == 3:
            wobbler.set_pixels(pixels, n_pixels_per_string, effective_time)

        client.put_pixels(pixels, channel=0)

        frame_duration = time.time() - frame_start
        frame_delay = 1.0 / fps

        if frame_delay > frame_duration:
          time.sleep(frame_delay - frame_duration)

if __name__ == "__main__":
    main()
