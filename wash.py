from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import opc
import color_utils

import pattern_utils
import palette_utils

def set_pixels(pixel_buff, pixels_per_string, elapsed_time, palette):
    for ii in range(len(pixel_buff)):
        palette_pixel_offset = palette_utils.get_total_offset(elapsed_time, ii, pixels_per_string, palette.len)
        pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], palette.vals[palette_pixel_offset], 0.5)
