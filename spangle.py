from __future__ import division
import random
import numpy
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import opc
import color_utils

import pattern_utils
import palette_utils

initialised = False
sparkle_offset = []

last_sparkle = 0

def init(n_pixels, time):
    global initialised
    global sparkle_offset
    global sparkle_time
    global last_sparkle

    initialised = True
    sparkle_offset = list(0.0 for i in range(n_pixels))
    last_sparkle = time

def set_pixels(pixel_buff, pixels_per_string, sparkle_chance, max_concurrent_sparkles, sparkle_fade_val, elapsed_time, palette, audio_level, audio_respond, colour_mash, fade_level):
    global sparkle_offset
    global sparkle_time
    global last_sparkle

    if not initialised:
        return

    since_last_sparkle = elapsed_time-last_sparkle

    if since_last_sparkle == 0:
        sparkle_chance = 0
    else:
        sparkle_chance *= 1.0/((since_last_sparkle*2) ** 2)

    # account for number of total pixels
    # sparkle_chance *= ((len(pixel_buff) / pixels_per_string) / 32)

    last_sparkle = elapsed_time

    for ii in range(max_concurrent_sparkles+1):
        if random.random() < sparkle_chance:
            sparkle_index = random.randint(0, len(sparkle_offset)-1)
            sparkle_offset[sparkle_index] = numpy.random.randn() * palette.len/2

    for ii in range(len(pixel_buff)):
        pixel_level = 1

        if audio_respond:
            pixel_index = ii % pixels_per_string
            pixel_response_proportion = (float(pixel_index) / pixels_per_string) ** 3.5
            pixel_level = (1-pixel_response_proportion) + (pixel_response_proportion * audio_level)

        pixel_val = tuple(pixel_level * channel * fade_level for channel in palette_utils.get_value(elapsed_time/2, ii+sparkle_offset[ii], pixels_per_string, palette, colour_mash))
        pixel_buff[ii] = pixel_val
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_val, 0.5)

        sparkle_offset[ii] *= sparkle_fade_val
