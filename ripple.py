from __future__ import division
import math
import time
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import opc
import color_utils

import pattern_utils
import palette_utils

def set_pixels(pixel_buff, pixels_per_string, elapsed_time, palette, fade_level):
    for ii in range(len(pixel_buff)):
        pixel_level = 1

        pixel_index = ii % pixels_per_string
        ripple_level = math.sin(pixel_index - time.time()*5)/2 + 0.5
        pixel_val = tuple(pixel_level * channel * ripple_level for channel in palette_utils.get_value(elapsed_time, ii, pixels_per_string, palette, False))
        pixel_buff[ii] = tuple(pixel_val[channel] * fade_level + pixel_buff[ii][channel] * (1.0-fade_level) for channel in range(3))
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_val, 0.5)
