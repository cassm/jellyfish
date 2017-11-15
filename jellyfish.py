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
import select

import threading

##############################

import colours
import pattern_utils
import palette_utils
from palette_utils import Palette

import segments
import spiral
import sparkle
import spangle
import ripple
import wash
import warp
import rainbow_waves
import wobbler
import web

import palettes

##############################

n_pixels_per_string = 50
n_strings = 16
n_pixels = n_strings * n_pixels_per_string

fps = 60

pixels = [(0.0, 0.0, 0.0) for i in range(n_pixels)]

command_input = []
last_sparkle = 0
warp_just_pressed = 0
fade_state = 0
fade_max = 0.9
fade_level = fade_max
segment_mix_level = 0.0
ripple_mix_level = 0.0
fade_down_step = 0.95
fade_up_step = 1.012
fade_threshold = 0.5

mut = threading.Lock()

def input_worker():
    global command_input
    global fade_state

    while True:
        x = raw_input()
        mut.acquire(True)
        try:
            command_input.append(x)
        finally:
            mut.release()

def main():
    global pixels
    global command_input
    global fade_state
    global fade_level
    global segment_mix_level
    global ripple_mix_level
    global last_sparkle
    global warp_just_pressed

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

    sparkle.init(n_pixels, time.time())
    spangle.init(n_pixels, time.time())
    warp.init(n_strings)
    web.init(n_strings)

    print('\tPolling input...')
    input_t = threading.Thread(target=input_worker)
    input_t.daemon = True
    input_t.start()

    # send pixels
    print('\tsending pixels forever (control-c to exit)...\n')

    while True:
        # process input
        if mut.acquire(False):
            try:
                if len(command_input) > 0:
                    print command_input
                    for x in command_input:
                        if "0" in x:
                            print "sparkle"
                            fade_state = 1
                            last_sparkle = time.time()
                        if "1" in x:
                            print "warp"
                            fade_state = 1
                            warp_just_pressed = True
                        if "2" in x:
                            print "segments"
                            segment_mix_level = 1.0
                        if "3" in x:
                            print "ripple"
                            ripple_mix_level = 1.0

                        print x

                    command_input = []
            finally:
                mut.release()

        if fade_state == 1:
            fade_level *= fade_down_step
            if fade_level < fade_threshold:
                fade_level = fade_threshold
                fade_state = 2

        elif fade_state == 2:
            fade_level *= fade_up_step
            if fade_level >= fade_max:
                fade_level = fade_max
                fade_state = 0

        segment_mix_level *= 0.992
        ripple_mix_level *= 0.992

        frame_start = time.time()

        current_palette = palettes.auto

        spangle.set_pixels(pixels, n_pixels_per_string, 0.0005, 1, 0.9999, time.time(), current_palette, 1.0, False, False, fade_level)

        segments.set_pixels(pixels, n_pixels_per_string, time.time(), current_palette, 1.0, False, False, segment_mix_level)

        # wash.set_pixels(pixels, n_pixels_per_string, time.time(), current_palette, 1.0, False, False, 0.6)
        ripple.set_pixels(pixels, n_pixels_per_string, time.time(), current_palette, ripple_mix_level)

        sparkle_chance = (1.0/(((time.time() - last_sparkle)*2)**2)) * 3
        if sparkle_chance < 0.1:
            sparkle_chance = 0

        # sparkle_chance = (max((1.0 - (time.time() - last_sparkle)**2), 0))

        sparkle.set_pixels(pixels, n_pixels_per_string, sparkle_chance, 10,
            time.time(), current_palette, 1.0, False, False, True)

        warp.set_pixels(pixels, n_pixels_per_string, 0, 0,
            time.time(), current_palette, False, False, False, True, warp_just_pressed)
        warp_just_pressed = False

        '''
        elif mode_id == 2:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, True,
                effective_time, current_palette, audio_level, audio_respond, colour_mash)

        elif mode_id == 3:
            spiral.set_pixels(pixels, n_pixels_per_string, n_strings, 2, False,
                effective_time, current_palette, audio_level, audio_respond, colour_mash)

        elif mode_id == 4:
            rainbow_waves.set_pixels(pixels, n_pixels_per_string,
                effective_time, 29, -13, 19, current_palette, audio_level, audio_respond, colour_mash)

        elif mode_id == 5:
            wobbler.set_pixels(pixels, n_pixels_per_string, effective_time,
                current_palette, beats_since_last > 0, audio_level, audio_respond, colour_mash)


        elif mode_id == 7:
            web.set_pixels(pixels, n_pixels_per_string, effective_time, current_palette, audio_level, audio_respond, colour_mash)
        '''

        client.put_pixels(pixels, channel=0)

        frame_duration = time.time() - frame_start
        frame_delay = 1.0 / fps

        if frame_delay > frame_duration:
          time.sleep(frame_delay - frame_duration)

if __name__ == "__main__":
    main()
