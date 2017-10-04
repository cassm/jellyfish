import math

def get_time_offset(elapsed_time, palette_len):
    time_factor = palette_len/-50
    return int(elapsed_time*time_factor) % palette_len

def get_space_offset(pixel_index, pixels_per_string, palette_len):
    palette_offset_per_pixel = (palette_len/20) / pixels_per_string
    return int((pixel_index % pixels_per_string) * palette_offset_per_pixel) % palette_len

def get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette_len):
    return (get_time_offset(elapsed_time, palette_len) + get_space_offset(pixel_index, pixels_per_string, palette_len)) % palette_len

def get_value(elapsed_time, pixel_index, pixels_per_string, palette, colour_mash):
    offset = get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette.len)
    val = palette.vals[offset]

    if colour_mash:
        mix_level = 0.1

        string_index = pixel_index % pixels_per_string
        shimmer_level = (sum(val) * mix_level) / 255.0

        long_time_coefficients = [0.081725, 0.123267, 0.368365]
        short_time_coefficients = [1.12, 2.001, 1.98]

        short_mix_factor = 0.25

        short_level = list(math.sin(elapsed_time * coefficient + string_index * 5) * short_mix_factor for coefficient in short_time_coefficients)
        long_level = list(math.sin(elapsed_time * coefficient + string_index * 5) * (1-short_mix_factor) for coefficient in long_time_coefficients)
        additive_val = list(255.0 * (short_level[i] + long_level[i]) for i in range(3))

        val = tuple(val[channel] * (1 - shimmer_level) + additive_val[channel] * shimmer_level for channel in range(3))

    return val

class Palette:
    def __init__(self, len, vals):
        self.len = len
        self.vals = vals
