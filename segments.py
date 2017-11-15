from __future__ import division
import time
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import opc
import color_utils

import pattern_utils
import palette_utils

def get_time_offset(elapsed_time, palette_len):
    time_factor = palette_len/-50
    return int(elapsed_time*time_factor) % palette_len

def get_space_offset(pixel_index, pixels_per_string, palette_len, segment_offset):
    palette_offset_per_pixel = (palette_len/20) / pixels_per_string
    return int(((pixel_index % pixels_per_string)+segment_offset) * palette_offset_per_pixel) % palette_len

def get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette_len, segment_offset):
    return (get_time_offset(elapsed_time, palette_len) + get_space_offset(pixel_index, pixels_per_string, palette_len, segment_offset)) % palette_len

def get_value(elapsed_time, pixel_index, pixels_per_string, palette, segment_offset):
    offset = get_space_offset(pixel_index, pixels_per_string, palette.len, segment_offset)
    val = palette.vals[offset]

    return val

def set_pixels(pixel_buff, pixels_per_string, elapsed_time, palette, audio_level, audio_respond, colour_mash, mix_level):
    for ii in range(len(pixel_buff)):
        pixel_level = 1

        if audio_respond:
            pixel_index = ii % pixels_per_string
            pixel_response_proportion = (float(pixel_index) / pixels_per_string) ** 1.2
            pixel_level = (1-pixel_response_proportion) + (pixel_response_proportion * audio_level)

        segment_num = int(((ii-time.time()*5)%pixels_per_string) / 5)
        offset_in_segment = ((ii-time.time()*5)%pixels_per_string) % 5
        offset_per_segment = palette.len/7.38
        segment_offset = segment_num * offset_per_segment

        pixel_val = tuple(pixel_level * channel for channel in get_value(elapsed_time/3, offset_in_segment*2, pixels_per_string, palette, segment_offset))

        pixel_buff[ii] = tuple(pixel_val[channel] * mix_level + pixel_buff[ii][channel] * (1.0-mix_level) for channel in range(3))
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], pixel_val, 0.5)
