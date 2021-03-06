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

def set_pixels(pixel_buff, pixels_per_string, num_strings, waves_per_string, add_spiral, elapsed_time, palette, audio_level, audio_respond, colour_mash):
    for ii in range(len(pixel_buff)):
        pixel_index = float(ii) % pixels_per_string
        string_index = float(ii) / pixels_per_string

        scaling_factor = math.pi*2 / pixels_per_string * waves_per_string

        spiral_offset = 0

        if add_spiral:
            spiral_offset = (float(string_index) / num_strings) * math.pi*2

        upshift = 0.55
        if audio_respond:
            upshift = math.sqrt(audio_level)/3 + 0.33

        brightness_level = min((math.sin(-elapsed_time +
          pixel_index*scaling_factor + spiral_offset) / 1.82) + upshift,
          1.55)

        if audio_respond:
            brightness_level *= min(math.sqrt(audio_level) + 0.35, 1)

        pixel_value = palette_utils.get_value(elapsed_time, ii, pixels_per_string, palette, colour_mash)
        pixel_value = tuple(brightness_level * channel / 255 for channel in pixel_value)

        pixel_value = tuple (channel * 255 for channel in color_utils.gamma(pixel_value, 2.2))

        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_value, 0.5)
        pixel_buff[ii] = pixel_value
