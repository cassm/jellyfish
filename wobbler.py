pixel_order = 0
last_pixel_order_switch = 0
min_pixel_order_switch_interval = 5

def set_pixels(pixels, elapsed_time):
    global pixel_order
    global last_pixel_order_switch

    n_pixels = len(pixels)

    time_cos_factor = 2
    wobble_amplitude = 5
    band_radius = pixels_per_string/2 + math.cos(time.time()/time_cos_factor)*18 - 13
    colour_offset = 3.14/6
    cos_factor = 6*3.14/(n_pixels/pixels_per_string)
    t = elapsed_time*4
    offset_ordering = [ [ 0, 1, 2], [0, 2, 1], [1, 0, 2] ]

    if math.cos(time.time()/time_cos_factor) < -0.99 and time.time() - last_pixel_order_switch > min_pixel_order_switch_interval:
        pixel_order = (pixelOrder + 1) % len(offset_ordering)
        last_pixel_order_switch = time.time()

    for string in range(n_strings):
        bandLocation = tuple(band_radius + wobble_amplitude*math.cos(t + string*cos_factor + colour_offset*offset_ordering[pixel_order][colour]) for colour in range(3))
        for pixel in range(pixels_per_string):
            pixCol = [0, 0, 0]
            for colour in range(3):
                distance = bandLocation[colour] - pixel
                if distance < 0:
                    distance *= -1

                pixCol[colour] = (2 + max(band_radius, 0.0000001)/10)/distance

            r, g, b = color_utils.gamma(pixCol, 2.2)
            pixels[string*pixels_per_string + pixel] = fadeDownTo(pixels[string*pixels_per_string + pixel], (g*255, r*255, b*255), 0.5)
