from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import random
import math
import opc
import color_utils

import pattern_utils
import palette_utils

initialised = False
sparkle_colour = []
sparkle_time = []

def init(n_pixels):
    global initialised
    global sparkle_colour
    global sparkle_time

    initialised = True
    sparkle_colour = list((0.0, 0.0, 0.0) for i in range(n_pixels))
    sparkle_time = list(0.0 for i in range(n_pixels))

def set_pixels(pixel_buff, pixels_per_string, sparkle_chance, max_concurrent_sparkles, elapsed_time, palette):
    global sparkle_colour
    global sparkle_time

    if not initialised:
        return

    for ii in range(max_concurrent_sparkles+1):
        if random.random() < sparkle_chance:
            sparkle_index = random.randint(0, len(sparkle_time)-1)
            palette_pixel_offset = palette_utils.get_total_offset(elapsed_time, sparkle_index, pixels_per_string, palette.len)
            sparkle_time[sparkle_index] = elapsed_time
            sparkle_colour[sparkle_index] = palette.vals[palette_pixel_offset]

    for ii in range(len(pixel_buff)):
        sparkle_intensity = min(pattern_utils.inverse_square(elapsed_time, sparkle_time[ii], 1.2), 1)
        pixel_value = tuple(channel * sparkle_intensity for channel in sparkle_colour[ii])

        pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_value, 0.5)
