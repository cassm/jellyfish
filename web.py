from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import math
import opc
import color_utils

import pattern_utils
import palette_utils

string_levels = []
string_brightness = []

def init(n_strings):
    global string_levels
    global string_brightness
    string_levels = list(0.0 for i in range(n_strings))
    string_brightness = list(0.75 for i in range(n_strings))

def set_pixels(pixels, pixels_per_string, elapsed_time, palette, audio_level, audio_respond, colour_mash):
    global string_levels
    global string_brightness

    '''
    if audio_respond:
        if beat_now:
            pixel_order = (pixel_order + 1) % len(offset_ordering)
            last_pixel_order_switch = elapsed_time

    else:
        if math.cos(elapsed_time/time_cos_factor) < -0.99 and elapsed_time - last_pixel_order_switch > min_pixel_order_switch_interval:
            pixel_order = (pixel_order + 1) % len(offset_ordering)
            last_pixel_order_switch = elapsed_time

    time_cos_factor = 2
    wobble_amplitude = 5
    band_radius = pixels_per_string/2 + math.cos(elapsed_time/time_cos_factor)*18 - 13
    colour_offset = 3.14/6
    cos_factor = 6*3.14/(n_pixels/pixels_per_string)
    '''

    n_pixels = len(pixels)
    n_strings = int(n_pixels / pixels_per_string)
    n_peaks = 3
    time_factor = -3
    amplitude_factor = 15 + 5*math.sin(elapsed_time * -0.5)

    for string in range(n_strings):
        radial_offset = (n_peaks*2*math.pi/n_strings) * string
        lateral_offset = math.sin(radial_offset + elapsed_time*time_factor) * amplitude_factor

        if lateral_offset > string_levels[string]:
            string_levels[string] = lateral_offset
            string_brightness[string] += (1.0 - string_brightness[string])*0.1
        else:
            string_levels[string] *= 0.98
            string_brightness[string] *= 0.98


        midpoint = (pixels_per_string/2.0 - 1) + (pixels_per_string/4)*math.sin(elapsed_time * -0.5)

        for pixel in range(pixels_per_string):
            palette_val = palette_utils.get_value(elapsed_time, pixel, pixels_per_string, palette, colour_mash)
            if pixel > midpoint - string_levels[string]:
                pixels[string*pixels_per_string + pixel] = tuple(channel*string_brightness[string] for channel in palette_val)
            else:
                pixels[string*pixels_per_string + pixel] = (0,0,0)


