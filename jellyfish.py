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
import palette_utils
from palette_utils import Palette

import spiral
import sparkle
import wash
import warp

import rainbow_waves
import wobbler

import palettes

##############################

n_pixels_per_string = 50
n_strings = 8
n_pixels = n_strings * n_pixels_per_string

manual_palette = Palette(10000, [])

last_manual_palette_sample = 0

fps = 60

last_measured_time = time.time()
effective_time = time.time()

pixels = [(0.0, 0.0, 0.0) for i in range(n_pixels)]
current_rgb_setting = (0, 0, 0)

speed_val = 1
mode_id = 0
last_mode_id = 0
audio_level = 0.5
audio_respond = True
auto_colour = False
colour_mash = False
mode_cycle = False
beats_since_last = 0

def get_bit(byteval,idx):
      return ((byteval&(1<<idx))!=0)

def process_dmx_frame(data):
    global speed_val
    global mode_id
    global audio_level
    global audio_respond
    global beats_since_last
    global auto_colour
    global colour_mash
    global mode_cycle
    global current_rgb_setting

    if len(data) != 8:
        return

    speed_val = data[0]/32.0
    mode_id = data[1]
    audio_level = data[2] / 255.0

    beat_now = get_bit(data[3], 4)

    if beat_now:
        beats_since_last += 1

    auto_colour = get_bit(data[3], 3)
    colour_mash = get_bit(data[3], 2)
    audio_respond = get_bit(data[3], 1)
    mode_cycle = get_bit(data[3], 0)

    current_rgb_setting = (data[4], data[5], data[6])

update_manual_palette_called = False

def update_manual_palette(current_time, value):
    global manual_palette
    global last_manual_palette_sample
    global update_manual_palette_called

    last_index = palette_utils.get_time_offset(last_manual_palette_sample, manual_palette.len)
    new_index = palette_utils.get_time_offset(current_time, manual_palette.len)

    if not update_manual_palette_called:
        # first call

        manual_palette.vals = list(value for i in range(manual_palette.len + 1))
        last_manual_palette_sample = current_time
        update_manual_palette_called = True

    elif last_index == new_index:
        # time has stopped
        pass

    else:
        # time is moving forwards

        if new_index < last_index:
            for i in range(new_index, last_index+1):
                manual_palette.vals[i] = value

            last_manual_palette_sample = current_time

        else:
            # wrap case
            for i in range(new_index, manual_palette.len+1):
                manual_palette.vals[i] = value
            for i in range(0, last_index):
                manual_palette.vals[i] = value

            last_manual_palette_sample = current_time

def main():
    global pixels
    global beats_since_last
    global last_measured_time
    global effective_time
    global last_mode_id
    global audio_level

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
    warp.init(n_strings)

    # send pixels
    print('\tsending pixels forever (control-c to exit)...\n')

    while True:
        frame_start = time.time()

        # update effective time in line with speed value
        effective_time += (time.time() - last_measured_time) * speed_val
        last_measured_time = time.time()

        # check for new dmx frames
        readable, writable, exceptional = select.select([sock], [], [], 0)
        while readable:
            ola_client.SocketReady()
            readable, writable, exceptional = select.select([sock], [], [], 0)

        update_manual_palette(effective_time, current_rgb_setting)

        if last_mode_id != mode_id:
            print "Mode switch {} -> {}".format(last_mode_id, mode_id)
            last_mode_id = mode_id

        current_palette = manual_palette

        if auto_colour:
          current_palette = palettes.auto

        if mode_id == 0:
            wash.set_pixels(pixels, n_pixels_per_string, effective_time, current_palette, audio_level, audio_respond)

        elif mode_id == 1:
            sparkle.set_pixels(pixels, n_pixels_per_string, 0.5, 5,
                effective_time, current_palette, audio_level, audio_respond)

        elif mode_id == 2:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, True,
                effective_time, current_palette, audio_level, audio_respond)

        elif mode_id == 3:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, False,
                effective_time, current_palette, audio_level, audio_respond)

        elif mode_id == 4:
            rainbow_waves.set_pixels(pixels, n_pixels_per_string,
                effective_time, 29, -13, 19, current_palette, audio_level, audio_respond)

        elif mode_id == 5:
            wobbler.set_pixels(pixels, n_pixels_per_string, effective_time, current_palette, audio_level, audio_respond)

        elif mode_id == 6:
            warp.set_pixels(pixels, n_pixels_per_string, 0.0625, 2,
                effective_time, current_palette, beats_since_last > 0, audio_respond)

        client.put_pixels(pixels, channel=0)

        frame_duration = time.time() - frame_start
        frame_delay = 1.0 / fps

        beats_since_last = 0

        if frame_delay > frame_duration:
          time.sleep(frame_delay - frame_duration)

if __name__ == "__main__":
    main()
