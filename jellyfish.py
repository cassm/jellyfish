#!/usr/bin/env python

"""
Spatialised LED pattern generator.

Based on a demo client for Open Pixel Control
http://github.com/zestyping/openpixelcontrol

Creates a shifting rainbow plaid pattern by overlaying different sine waves
in the red, green, and blue channels.

To run:
First start the gl simulator using the included "wall" layout

    make
    bin/gl_server layouts/wall.json

Then run this script in another shell to send colors to the simulator

    python_clients/raver_plaid.py

"""

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
import colours

##############################

import getopt
import textwrap
import sys
from ola import OlaClient
import select

import threading

brightnessValue = 0

def NewData(data):
  global brightnessValue
  brightnessValue = data[0]

# use for mode switching. Modes are as follows:
# 0: chill
# 1: dance
# 2: rain
# 3: lava lamp
# 4: rainbow sparkles
# 5: wobbler

patternNumber = 0

patternDict = { 'C': 0, 'D': 1, 'R': 2, 'L': 3, 'S': 4, 'W': 5 }

maxPatternNumber = 6

n_pixels = 2  # number of pixels in the included "wall" layout
n_strings = 16
pixels_per_string = int(n_pixels/n_strings)

fps = 60         # frames per second

start_time = time.time()

pixels = [(0.0, 0.0, 0.0) for i in range(n_pixels)]

def fadeDownTo(fromVal, toVal, step):
    result = [0.0, 0.0, 0.0]

    for colour in range(3):
        if fromVal[colour] != toVal[colour]:
            diff = fromVal[colour] - toVal[colour]
            result[colour] = fromVal[colour] - diff*step
        else:
            result[colour] = toVal[colour]

    return tuple(result)

def rainbowWaves(speed_r, speed_g, speed_b):
    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 24
    freq_g = 24
    freq_b = 24

    t = (time.time() - start_time) * 5

    for ii in range(n_pixels):
        pct = (ii / n_pixels)
        # diagonal black stripes
        pct_jittered = (pct * 77) % 37
        blackstripes = color_utils.cos(pct_jittered, offset=t*0.05, period=1, minn=-1.5, maxx=1.5)
        blackstripes_offset = color_utils.cos(t, offset=0.9, period=60, minn=-0.5, maxx=3)
        blackstripes = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)
        # 3 sine waves for r, g, b which are out of sync with each other
        r = blackstripes * color_utils.remap(math.cos((t/speed_r + pct*freq_r)*math.pi*2), -1, 1, 0, 256)
        g = blackstripes * color_utils.remap(math.cos((t/speed_g + pct*freq_g)*math.pi*2), -1, 1, 0, 256)
        b = blackstripes * color_utils.remap(math.cos((t/speed_b + pct*freq_b)*math.pi*2), -1, 1, 0, 256)
        pixels[ii] = fadeDownTo(pixels[ii], (r, g, b), 0.5)

def faderTest():
  for ii in range(n_pixels):
      pixels[ii] = (brightnessValue, brightnessValue, brightnessValue)

class DmxReceiver(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=0.01):
        """ Constructor
        :type interval: int
        :param interval: Check interval,
        in seconds
        """
        wrapper = ClientWrapper()
        client = wrapper.Client()
        client.RegisterUniverse(1, client.REGISTER, NewData)

        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True # Daemonize thread
        thread.start() # Start the execution

    def run(self):
        wrapper.Run()

def main():
    global patternNumber
    global udpInitialised

    # receiver = DmxReceiver()

    ola_client = OlaClient.OlaClient()
    sock = ola_client.GetSocket()
    ola_client.RegisterUniverse(1, ola_client.REGISTER, NewData)

    #-------------------------------------------------------------------------------
    # handle command line

    parser = optparse.OptionParser()
    parser.add_option('-l', '--layout', dest='layout', default='disc.json',
                      action='store', type='string',
                      help='layout file')
    parser.add_option('-s', '--server', dest='server', default='127.0.0.1:7890',
                      action='store', type='string',
                      help='ip and port of server')

    options, args = parser.parse_args()

    #-------------------------------------------------------------------------------
    # parse layout file

    print
    print '    parsing layout file'
    print

    coordinates = []
    for item in json.load(open(options.layout)):
        if 'point' in item:
            coordinates.append(tuple(item['point']))

    #-------------------------------------------------------------------------------
    # connect to server

    client = opc.Client(options.server)
    if client.can_connect():
        print('    connected to %s' % options.server)
    else:
        # can't connect, but keep running in case the server appears later
        print('    WARNING: could not connect to %s' % options.server)
    print('')


    #-------------------------------------------------------------------------------
    # send pixels

    print('    sending pixels forever (control-c to exit)...')
    print('')

    nextDrop = 0.0

    while True:
        readable, writable, exceptional = select.select([sock], [], [], 0)
        if readable: # tell it ola_client
            ola_client.SocketReady()

        # rainbowWaves(29, -13, 19)

        print(brightnessValue)
        faderTest()

        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

if __name__ == "__main__":
    main()
