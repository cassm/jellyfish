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
last_beat_detected = time.time()

class Spark:
    def __init__(self, palette, pixels_per_string, time, colour_mash):
        self.colour = palette_utils.get_value(time, 0, 10, palette, colour_mash)
        self.time = time
        self.pixels_per_string = pixels_per_string
        self.active = True

    def get_val(self, index, elapsed_time):
        string_index = index % self.pixels_per_string
        pos = (elapsed_time - self.time) * self.pixels_per_string/1.5
        if string_index < pos:
            brightness_factor = min(1.0 / (((pos - string_index)/3)**2), 1.5)
            val = tuple(int(brightness_factor * channel) for channel in self.colour)
            if string_index == self.pixels_per_string-1 and val == (0,0,0):
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

shot_index = 0

def set_pixels(pixel_buff, pixels_per_string, spark_chance, max_concurrent_sparks, elapsed_time, palette, beat_detected, audio_respond, colour_mash, add, force_sparks):
    global sparks
    global shot_index
    global last_beat_detected

    if not initialised:
        return

    # if audio_respond:
    #     max_concurrent_sparks = max(int(warp_n_strings * (audio_level**2)), 1)
    #     spark_chance = max((audio_respond**2), spark_chance/4)

    if (force_sparks):
        for x in range(len(sparks)):
            sparks[x].append(Spark(palette, pixels_per_string, elapsed_time, False))

    elif (audio_respond):
        spark_chance /= 2

        if beat_detected:
            shot_index_1 = int(shot_index % warp_n_strings)
            shot_index_2 = int((shot_index + warp_n_strings/2) % warp_n_strings)

            sparks[shot_index_1].append(Spark(palette, pixels_per_string,
              elapsed_time, colour_mash))
            sparks[shot_index_2].append(Spark(palette, pixels_per_string,
              elapsed_time, colour_mash))

            shot_index += 1
            last_beat_detected = time.time()

        if last_beat_detected + 1 < time.time():
            for ii in range(max_concurrent_sparks+1):
                if random.random() < spark_chance:
                    strand = random.randint(0, len(sparks)-1)
                    sparks[strand].append(Spark(palette, pixels_per_string,
                      elapsed_time, colour_mash))

    else:
        for ii in range(max_concurrent_sparks+1):
            if random.random() < spark_chance:
                strand = random.randint(0, len(sparks)-1)
                sparks[strand].append(Spark(palette, pixels_per_string,
                  elapsed_time, colour_mash))

    for ii in range(len(pixel_buff)):
        strand_id = int(ii / pixels_per_string)

        val = [0, 0, 0]

        for spark in sparks[strand_id]:
            spark_val = spark.get_val(ii, elapsed_time)
            if sum(spark_val) > sum(val):
                val = spark_val

        if add:
            pixel_buff[ii] = tuple(max(val[channel], pixel_buff[ii][channel]) for channel in range(3))
        else:
            pixel_buff[ii] = val

    for ii in range(len(sparks)):
        sparks[ii] = list(spark for spark in sparks[ii] if spark.active)
