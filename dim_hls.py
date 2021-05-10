import lightpack, configparser, os, colorsys
from dithering import *
from time import sleep
from PIL import Image

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

# Load config
script_dir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(script_dir + '/DimThis.ini')

# Load Lightpack settings
lightpack_host = config.get('Lightpack', 'host')
lightpack_port = config.getint('Lightpack', 'port')
lightpack_api_key = config.get('Lightpack', 'key')
lightpack_profile = config.get('Lightpack', 'profile')

lp = lightpack.lightpack(lightpack_host, lightpack_port, None, lightpack_api_key)
lp.connect()

num_leds = lp.getCountLeds()

brightness_dim = 0.6
start_color = colorsys.rgb_to_hls(255/255, 135/255, 55/255)
end_color = colorsys.rgb_to_hls((255 * brightness_dim)/255, (106 * brightness_dim)/255, (0 * brightness_dim)/255)
steps = 256

gamma = 1.0
B_START = start_color[1] ** (1 / gamma)
B_END = end_color[1] ** (1 / gamma)

img = Image.new('RGB', (steps, num_leds))
ld = img.load()

lp.lock()

for i in range(steps):
    scale = i / steps
    # h = scale_linear(start_color[0], end_color[0], scale)
    # l = scale_linear(start_color[1], end_color[1], scale)
    # s = scale_linear(start_color[2], end_color[2], scale)

    B = scale_linear(B_START, B_END, scale)
    h = start_color[0]
    l = B ** gamma
    s = start_color[2]

    r, g, b = tuple(i * 255 for i in colorsys.hls_to_rgb(h, l, s))

    # print(B)
    print(((0.299 * r / 255) ** gamma + (0.587 * g / 255) ** gamma + (0.114 * b / 255) ** gamma) ** (1 / gamma))
    # print(r, g, b)

    frame = dither(r, g, b, num_leds)

    # generate gradient image
    for y in range(num_leds):
        ld[i, y] = frame[y]

    lp.setFrame(frame)
    sleep(0.1)

# gaussian blur
# blur = Image.new('RGB', (img.size[0] - 2, img.size[1]))
# ld_b = blur.load()
# for x in range(blur.size[0]):
#     for y in range(blur.size[1]):
#         ld_b[x, y] = tuple(map(lambda i, j, k: round((i + j + k) / 3), ld[x, y], ld[x + 1, y], ld[x + 2, y]))

img.save('dim_hls.png')
sleep(5)

lp.unlock()
