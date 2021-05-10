import lightpack, configparser, os, colorsys
from time import sleep
from PIL import Image

# scale in [0, 1]
def scale_smooth_cubic(start, end, scale):
    return -2 * (end - start) * (scale ** 3) + 3 * (end - start) * (scale ** 2) + start

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

brightness_dim = 0.6
start_color = (17, 200, 255)
end_color = (17, 255, 255 * brightness_dim)
steps = 400

img = Image.new('RGB', (steps, int(steps / 2)))
ld = img.load()

lp.lock()

for i in range(steps):
    scale = i / steps
    h = scale_smooth_cubic(start_color[0], end_color[0], scale)
    s = scale_smooth_cubic(start_color[1], end_color[1], scale)
    v = scale_smooth_cubic(start_color[2], end_color[2], scale)

    r, g, b = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/255, s/255, v/255))

    print(r, g, b)

    # generate gradient image
    for y in range(img.size[1]):
        ld[i, y] = r, g, b

    # lp.setSmooth(255)
    lp.setColorToAll(r, g, b)
    sleep(0.1)

img.save('dim_hsv.png')
sleep(5)

lp.unlock()
