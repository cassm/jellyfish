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

last_sparkle = 0

def init(n_pixels, time):
    global initialised
    global sparkle_colour
    global sparkle_time
    global last_sparkle

    initialised = True
    sparkle_colour = list((0.0, 0.0, 0.0) for i in range(n_pixels))
    sparkle_time = list(0.0 for i in range(n_pixels))
    last_sparkle = time

def set_pixels(pixel_buff, pixels_per_string, sparkle_chance, max_concurrent_sparkles, elapsed_time, palette, audio_level, audio_respond, colour_mash, add):
    global sparkle_colour
    global sparkle_time
    global last_sparkle

    if not initialised:
        return

    since_last_sparkle = elapsed_time-last_sparkle

    # if since_last_sparkle == 0:
        # sparkle_chance = 0
    # else:
        # sparkle_chance *= 1.0/((since_last_sparkle*2) ** 2)

    last_sparkle = elapsed_time

    if audio_respond:
        max_concurrent_sparkles = max(int(max_concurrent_sparkles * (audio_level**2) * 5), 1)
        sparkle_chance = max(sparkle_chance * (audio_level**2) * 5, sparkle_chance/4)

    for ii in range(max_concurrent_sparkles+1):
        if random.random() < sparkle_chance:
            sparkle_index = random.randint(0, len(sparkle_time)-1)
            sparkle_time[sparkle_index] = elapsed_time
            sparkle_colour[sparkle_index] = palette_utils.get_value(elapsed_time, sparkle_index, pixels_per_string, palette, colour_mash)

    for ii in range(len(pixel_buff)):
        sparkle_intensity = min(1.0/((max(elapsed_time - sparkle_time[ii], 0.001))*3)**2, 1.5)
        # sparkle_intensity = min(pattern_utils.inverse_square(elapsed_time, sparkle_time[ii], 2.0), 1)
        pixel_value = tuple(channel * sparkle_intensity for channel in sparkle_colour[ii])
        #pixel_value = tuple(255 * channel for channel in color_utils.gamma(pixel_value, 2.2))

        if add:
            pixel_buff[ii] = tuple(max(pixel_value[channel], pixel_buff[ii][channel]) for channel in range(3))
        else:
            pixel_buff[ii] = pixel_value
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_value, 0.5)
