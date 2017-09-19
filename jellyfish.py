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
import rainbow_waves
import wobbler

##############################

n_pixels = 2
n_strings = 8
pixels_per_string = int(n_pixels/n_strings)

fps = 60

start_time = time.time()

pixels = [(0.0, 0.0, 0.0) for i in range(n_pixels)]

brightness_value = 0
mode_id = 0

def process_dmx_frame(data):
  global brightness_value
  brightness_value = data[0]

def faderTest():
  for ii in range(n_pixels):
      pixels[ii] = (brightness_value, brightness_value, brightness_value)

def main():
    global patternNumber
    global udpInitialised

    # initialise DMX slave listener
    ola_client = OlaClient.OlaClient()
    sock = ola_client.GetSocket()
    ola_client.RegisterUniverse(1, ola_client.REGISTER, process_dmx_frame)

    # handle command line
    parser = optparse.OptionParser()
    parser.add_option('-l', '--layout', dest='layout', default='disc.json',
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


    # send pixels

    print('\tsending pixels forever (control-c to exit)...\n')

    while True:
        # check for new dmx frames
        readable, writable, exceptional = select.select([sock], [], [], 0)
        if readable:
            ola_client.SocketReady()

        print(brightness_value)
        if mode_id == 0:
            faderTest()
        else if mode_id == 1:
            rainbow_waves.set_pixels(pixels, time.time() - start_time, 29, -13, 19)
        else if mode_id == 2:
            wobbler.set_pixels(pixels, time.time() - start_time)

        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

if __name__ == "__main__":
    main()
