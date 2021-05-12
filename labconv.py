
REFX = 95.047
REFY = 100.0
REFZ = 108.883

def within_range(value, min, max):
    if (value < min):
        value = min
    elif (value > max):
        value = max

    return value

def rgb_to_xyz(rgb):
    r, g, b = tuple(value / 255.0 for value in rgb)

    if (r > 0.04045):
        r = ((r + 0.055) / 1.055) ** 2.4
    else:
        r /= 12.92

    if (g > 0.04045):
        g = ((g + 0.055) / 1.055) ** 2.4
    else:
        g /= 12.92

    if (b > 0.04045):
        b = ((b + 0.055) / 1.055) ** 2.4
    else:
        b /= 12.92

    r *= 100.0
    g *= 100.0
    b *= 100.0

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return x, y, z

def lab_to_xyz(lab):
    y = (lab[0] + 16.0) / 116.0
    x = lab[1] / 500.0 + y
    z = y - lab[2] / 200.0

    if (x ** 3 > 0.008856):
        x = x ** 3
    else:
        x = (x - 16.0 / 116.0) / 7.787

    if (y ** 3 > 0.008856):
            y = y ** 3
    else:
        y = (y - 16.0 / 116.0) / 7.787

    if (z ** 3 > 0.008856):
            z = z ** 3
    else:
        z = (z - 16.0 / 116.0) / 7.787

    x, y, z = REFX * x, REFY * y, REFZ * z

    return x, y, z

def xyz_to_lab(xyz):
    x, y, z = xyz[0] / REFX, xyz[1] / REFY, xyz[2] / REFZ

    if (x > 0.008856):
        x = x ** (1.0 / 3.0)
    else:
        x = (7.787 * x) + (16.0 / 116.0)

    if (y > 0.008856):
            y = y ** (1.0 / 3.0)
    else:
        y = (7.787 * y) + (16.0 / 116.0)

    if (z > 0.008856):
        z = z ** (1.0 / 3.0)
    else:
        z = (7.787 * z) + (16.0 / 116.0)

    l = (116.0 * y) - 16.0
    a = within_range(500.0 * (x - y), -128, 127)
    b = within_range(200.0 * (y - z), -128, 127)

    return l, a, b

def xyz_to_rgb(xyz):
    x, y, z = tuple(value / 100.0 for value in xyz)

    r = x *	3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x *	0.0557 + y * -0.2040 + z * 1.0570

    if (r > 0.0031308):
        r = 1.055 * (r ** (1.0 / 2.4)) - 0.055
    else:
        r *= 12.92

    if (g > 0.0031308):
            g = 1.055 * (g ** (1.0 / 2.4)) - 0.055
    else:
        g *= 12.92

    if (b > 0.0031308):
            b = 1.055 * (b ** (1.0 / 2.4)) - 0.055
    else:
        b *= 12.92

    r, g, b = tuple(within_range(value, 0.0, 1.0) * 255.0 for value in (r, g, b))

    return r, g, b

# l in [0, 1] and a,b in [-128, 127]
def lab_to_rgb(lab):
    return xyz_to_rgb(lab_to_xyz(lab))

# r,g,b in [0, 255]
def rgb_to_lab(rgb):
    return xyz_to_lab(rgb_to_xyz(rgb))
