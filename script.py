import lightpack, configparser, os, colorsys
from datetime import datetime, timedelta
from time import sleep


class Dimmer:
    def __init__(self):
        self.load_config()
        self.lp = lightpack.lightpack(self.lightpack_host, self.lightpack_port, None, self.lightpack_api_key)
        self.lp.connect()

    def __del__(self):
        self.lp.disconnect()

    def load_config(self):
        # Load config
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config = configparser.ConfigParser()
        config.read(script_dir + '/DimThis.ini')

        # Load Lightpack settings
        self.lightpack_host = config.get('Lightpack', 'host')
        self.lightpack_port = config.getint('Lightpack', 'port')
        self.lightpack_api_key = config.get('Lightpack', 'key')
        self.lightpack_profile = config.get('Lightpack', 'profile')

        # Load settings
        self.time_start = [(int(i[1:]) if i[0] == '0' else int(i)) for i in config.get('Time', 'start').split(':')]
        self.dim_duration = config.getint('Time', 'duration')
        self.time_end = [(int(i[1:]) if i[0] == '0' else int(i)) for i in config.get('Time', 'end').split(':')]
        self.h = config.getint('Color', 'hue')
        self.s = config.getint('Color', 'saturation_standard')
        self.s_dim = config.getint('Color', 'saturation_dimmed')
        self.v = config.getint('Color', 'value_standard')
        self.v_dim = config.getint('Color', 'value_dimmend')
        self.brightness = config.getint('Brightness', 'standard')
        self.brightness_dim = config.getint('Brightness', 'dimmed')
   
    def dim_to(self, h, s, v, brightness):

        r, g, b = self.hsv_rgb(h, s, v)

        print((r, g, b), brightness)

        self.lp.lock()
        self.lp.setBrightness(round(brightness))
        self.lp.setColorToAll(r, g, b)
        self.lp.setPersistOnUnlock(True)
        self.lp.unlock()

    def hsv_rgb(self, h, s, v):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/255, s/255, v/255))

    def check_time(self):
        local_time = datetime.now()
        start_time = local_time.replace(hour=self.time_start[0], minute=self.time_start[1], second=0)
        end_time = local_time.replace(hour=self.time_end[0], minute=self.time_end[1], second=0)

        is_between = False

        # 1. case: spanning two days e.g. start 23:00 - end 02:00
        if end_time < start_time: 
            if local_time < end_time:
                # localtime is between 00:00 - end_time
                is_between = True
                start_time -= timedelta(days=1)
            else:
                # check if localtime is between start_time - 00:00
                is_between = local_time > start_time
                end_time += timedelta(days=1)
        # 2. case: spanning one day e.g. start 01:00 - end 07:00 <-> local 23:00
        elif local_time > end_time:
            start_time += timedelta(days=1)
            end_time += timedelta(days=1)
        elif local_time > start_time:
            # check if localtime is between start_time - end_time
            is_between = True

        return (is_between, abs(int((start_time - local_time).total_seconds())), abs(int((end_time - local_time).total_seconds())))

    def scale_linear(self, start, end, scale):
        return scale * end + (1 - scale) * start

    def run(self):
        while(True):
            if not (self.lp.getProfile().strip() == self.lightpack_profile):
                print("wrong profile: " + self.lp.getProfile().strip())
                break
            
            dim_on, start_diff, end_diff = self.check_time()

            if dim_on:
                if start_diff >= self.dim_duration * 60:
                    self.dim_to(self.h, self.s_dim, self.v_dim, self.brightness_dim)
                    print("sleep for ~" + str(end_diff / 120) + " minutes")
                    sleep(end_diff / 2 + 1)
                else:
                    # dimming process
                    scale = start_diff / (self.dim_duration * 60)

                    s_scale = self.scale_linear(self.s, self.s_dim, scale)
                    v_scale = self.scale_linear(self.v, self.v_dim, scale)
                    brightness_scaled = self.scale_linear(self.brightness, self.brightness_dim, scale)

                    self.dim_to(self.h, s_scale, v_scale, brightness_scaled)
                    sleep(0.1)#(self.dim_duration * 60) / max(abs(self.s - self.s_dim), abs(self.v - self.v_dim))) # in seconds
            else:
                self.dim_to(self.h, self.s, self.v, self.brightness)
                print("sleep for ~" + str(start_diff / 120) + " minutes")
                sleep(start_diff / 2 + 1)

dim = Dimmer()
dim.run()
