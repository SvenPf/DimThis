
def dither(r, g, b, num_leds):
    frame = []
    error_dr = 0
    error_dg = 0
    error_db = 0

    for i in range(num_leds):
        old_r = r + error_dr
        old_g = g + error_dg
        old_b = b + error_db

        new_r, new_g, new_b = tuple(0 if value < 0 else round(value) for value in (old_r, old_g, old_b))

        error_dr = old_r - new_r
        error_dg = old_g - new_g
        error_db = old_b - new_b

        frame.append((new_r, new_g, new_b))

    return frame
