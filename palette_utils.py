import math

def get_time_offset(elapsed_time, palette_len):
    time_factor = palette_len/-50
    return int(elapsed_time*time_factor) % palette_len

def get_space_offset(pixel_index, pixels_per_string, palette_len):
    palette_offset_per_pixel = (palette_len/10) / pixels_per_string
    return int((pixel_index % pixels_per_string) * palette_offset_per_pixel) % palette_len

def get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette_len):
    return (get_time_offset(elapsed_time, palette_len) + get_space_offset(pixel_index, pixels_per_string, palette_len)) % palette_len

def get_value(elapsed_time, pixel_index, pixels_per_string, palette, colour_mash):
    offset = get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette.len)
    val = palette.vals[offset]

    if colour_mash:
        mix_level = 0.1

        string_index = pixel_index % pixels_per_string
        shimmer_level = sum(val) * mix_level

        time_coefficients = [0.1725, 0.23267, 0.68365]

        additive_val = list(math.sin(elapsed_time * coefficient + string_index * 5)for coefficient in time_coefficients)

        if additive_val != 0:
            scaling_factor = shimmer_level / sum(additive_val)

            val = tuple(val[channel] * (1 - mix_level) + additive_val[channel] * scaling_factor for channel in range(3))

        return val

class Palette:
    def __init__(self, len, vals):
        self.len = len
        self.vals = vals
