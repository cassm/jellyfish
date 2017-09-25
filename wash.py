from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import opc
import color_utils

import pattern_utils
import palette_utils

def set_pixels(pixel_buff, pixels_per_string, elapsed_time, palette, audio_level, audio_respond):
    for ii in range(len(pixel_buff)):
        pixel_level = 1

        if audio_respond:
            pixel_index = ii % pixels_per_string
            pixel_response_proportion = (float(pixel_index) / pixels_per_string) ** 1.2
            pixel_level = (1-pixel_response_proportion) + (pixel_response_proportion * audio_level)

        palette_pixel_offset = palette_utils.get_total_offset(elapsed_time, ii, pixels_per_string, palette.len)

        pixel_val = tuple(pixel_level * channel for channel in palette.vals[palette_pixel_offset])
        pixel_buff[ii] = pixel_val
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_val, 0.5)
