from __future__ import division
import sys
import os
cwd = os.getcwd()

sys.path.insert(0, cwd+"/openpixelcontrol/python/")

import random
import math
import time
import opc
import color_utils

import pattern_utils
import palette_utils

initialised = False
first_run = True

class Spark:
    def __init__(self, palette, pixels_per_string, time):
        self.time = time
        self.pixels_per_string = pixels_per_string
        self.active = True
        self.palette = palette

    def get_val(self, index, time):
        string_index = index % self.pixels_per_string
        pos = (time - self.time) * self.pixels_per_string/3.0

        palette_pixel_offset = palette_utils.get_total_offset(time*4, 0, 10, self.palette.len)
        colour = self.palette.vals[palette_pixel_offset]

        if string_index < pos:
            brightness_factor = min(1.0 / ((pos - string_index)/2), 1)
            val = tuple(int(brightness_factor * channel) for channel in colour)
            if string_index == self.pixels_per_string-1 and max(val) < 5:
                self.active = False
            return val
        else:
            return (0,0,0)



warp_n_strings = 0
sparks = []

def init(n_strings):
    global initialised
    global warp_n_strings
    global sparks

    initialised = True
    warp_n_strings = n_strings
    sparks = list([] for i in range(n_strings))

def render(pixel_buff, pixels_per_string, elapsed_time, palette):
    global first_run
    global sparks

    if not initialised:
        return

    if (first_run):
        first_run = False

        for ii in range(warp_n_strings):
            sparks[ii].append(Spark(palette, pixels_per_string, elapsed_time))

    for ii in range(len(pixel_buff)):
        strand_id = int(ii / pixels_per_string)

        val = [0, 0, 0]

        for spark in sparks[strand_id]:
            spark_val = spark.get_val(ii, elapsed_time)
            if sum(spark_val) > sum(val):
                val = spark_val

        pixel_buff[ii] = val

    finished = True

    for ii in range(len(sparks)):
        sparks[ii] = list(spark for spark in sparks[ii] if spark.active)
        if len(sparks[ii]) > 0:
            finished = False

    return finished

