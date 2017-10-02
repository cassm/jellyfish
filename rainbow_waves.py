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

def set_pixels(pixel_buff, pixels_per_string, elapsed_time, speed_r, speed_g, speed_b, palette, audio_level, audio_respond):
    # how many sine wave cycles are squeezed into our n_pixels
    # 24 happens to create nice diagonal stripes on the wall layout
    freq_r = 24
    freq_g = 24
    freq_b = 24

    t = elapsed_time * 5
    n_pixels = len(pixel_buff)

    audio_factor = 1.0

    if audio_respond:
        audio_factor = 1.0

    for ii in range(n_pixels):
        pct = (ii / n_pixels)
        # diagonal black stripes
        pct_jittered = (pct * 77) % 37

        blackstripes = color_utils.cos(pct_jittered, offset=t*0.05, period=1, minn=-1.5, maxx=1.5)

        blackstripes_offset = color_utils.cos(t, offset=0.9, period=60, minn=-0.5, maxx=3)

        if audio_respond:
            root_lev = math.sqrt(audio_level)
            blackstripes = color_utils.clamp(blackstripes +
                blackstripes_offset, 0+root_lev/2, 0.5+root_lev/2)
        else:
            blackstripes = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)

        # 3 sine waves for r, g, b which are out of sync with each other
        r = blackstripes * color_utils.remap(math.cos((t/speed_r + pct*freq_r)*math.pi*2), -1, 1, 0, 256)
        g = blackstripes * color_utils.remap(math.cos((t/speed_g + pct*freq_g)*math.pi*2), -1, 1, 0, 256)
        b = blackstripes * color_utils.remap(math.cos((t/speed_b + pct*freq_b)*math.pi*2), -1, 1, 0, 256)
        # pixel_buff[ii] = pattern_utils.fadeDownTo(pixel_buff[ii], (r, g, b), 0.5)

        palette_pixel_offset = palette_utils.get_total_offset(elapsed_time, ii, pixels_per_string, palette.len)
        palette_val = palette.vals[palette_pixel_offset]
        r *= palette_val[0]/255.0
        g *= palette_val[1]/255.0
        b *= palette_val[2]/255.0

        pixel_buff[ii] = tuple(min(channel*audio_factor, 255) for channel in (r, g, b))
