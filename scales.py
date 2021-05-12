
# scale in [0, 1]
def scale_smooth_cubic(start, end, scale):
    return -2 * (end - start) * (scale ** 3) + 3 * (end - start) * (scale ** 2) + start

# scale in [0, 1]
def scale_cubic(start, end, scale):
    return 4 * (end - start) * (scale ** 3) - 6 * (end - start) * (scale ** 2) + 3 * (end - start) * scale + start

# scale in [0, 1]
def scale_quadratic(start, end, scale):
    return (start - end) * (scale ** 2) - 2 * (start - end) * scale + start

# scale in [0, 1]
def scale_linear(start, end, scale):
    return scale * end + (1 - scale) * start
