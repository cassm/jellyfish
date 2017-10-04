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

    n_pixels = len(pixels)
    n_strings = int(n_pixels / pixels_per_string)
    n_peaks = 3
    time_factor = -0.5
    amplitude_factor = 12.5 + 5*math.sin(elapsed_time * -0.2)

    for string in range(n_strings):
        radial_offset = (n_peaks*2*math.pi/n_strings) * string
        lateral_offset = math.sin(radial_offset + elapsed_time*time_factor) * amplitude_factor

        if lateral_offset > string_levels[string]:
            string_levels[string] = lateral_offset
            string_brightness[string] +=  (1.0 - string_brightness[string])*0.15

        else:
            string_levels[string] *= 0.95
            string_brightness[string] -= (string_brightness[string] - 0.25) * 0.075

        midpoint = ((8*pixels_per_string/12) - 1) + (pixels_per_string/2.5)*math.sin(elapsed_time * -0.5)

        brightness_val = string_brightness[string]

        for pixel in range(pixels_per_string):
            palette_val = palette_utils.get_value(elapsed_time, pixel, pixels_per_string, palette, colour_mash)

            pixel_level = 1.0

            if audio_respond:
                pixel_response_proportion = (1-(float(pixel) / pixels_per_string)) ** 1.2
                pixel_level = (1-pixel_response_proportion) + (pixel_response_proportion * audio_level)

            if pixel >= midpoint - string_levels[string]:
                pixels[string*pixels_per_string + pixel] = tuple(pixel_level*string_brightness[string]*channel for channel in palette_val)
            else:
                distance_from_midpoint = midpoint - pixel
                fade_factor = min(1.0/(distance_from_midpoint**2), 1)
                pixels[string*pixels_per_string + pixel] = tuple(fade_factor * string_brightness[string]*pixel_level*channel for channel in palette_val)
