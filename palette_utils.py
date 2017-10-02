def get_time_offset(elapsed_time, palette_len):
    time_factor = palette_len/-50
    return int(elapsed_time*time_factor) % palette_len

def get_space_offset(pixel_index, pixels_per_string, palette_len):
    palette_offset_per_pixel = (palette_len/10) / pixels_per_string
    return int((pixel_index % pixels_per_string) * palette_offset_per_pixel) % palette_len

def get_total_offset(elapsed_time, pixel_index, pixels_per_string, palette_len):
    return (get_time_offset(elapsed_time, palette_len) + get_space_offset(pixel_index, pixels_per_string, palette_len)) % palette_len

class Palette:
    def __init__(self, len, vals):
        self.len = len
        self.vals = vals
