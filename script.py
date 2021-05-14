import lightpack, labconv, scales, configparser, os, colorsys, random
from datetime import datetime, timedelta
from time import sleep

STEPS = 255

class DimThis:
    def __init__(self):
        self.load_config()
        self.lp = lightpack.lightpack(self.lightpack_host, self.lightpack_port, None, self.lightpack_api_key)
        self.lp.connect()
        self.lab = labconv.rgb_to_lab(tuple(i * 255.0 for i in colorsys.hsv_to_rgb(self.h / 255, self.s / 255, self.v / 255)))
        if self.randomize: self.lab_rand = self.make_rand_of(self.lab, self.closeness)
        self.gamma = float(self.lp.getGamma())
        self.brightness_start = self.lab[0] ** (1 / self.gamma)
        self.brightness_end = self.brightness_start * (self.dim_amount / 100)
        # print(self.lab, self.gamma, self.lum)

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
        self.trans_start = config.getint('Time', 'tstart')
        self.randomize = config.getboolean('Color', 'randomize')
        self.closeness = config.getint('Color', 'closeness')
        self.h = config.getint('Color', 'hue')
        self.s = config.getint('Color', 'saturation')
        self.v = config.getint('Color', 'value')
        self.dim_amount = config.getint('Dimming', 'amount')

    def set_color(self, lab):
        r, g, b = tuple(round(i) for i in labconv.lab_to_rgb(lab))
        print("set color to: ", (r, g, b))

        # self.lp.lock()
        self.lp.setColorToAll(r, g, b)
        # self.lp.setPersistOnUnlock(False)
        # self.lp.unlock()

    def make_rand_of(self, lab, distance):
        a_new = labconv.within_range(lab[1] + random.randint(-distance, distance), -128, 127)
        b_new = labconv.within_range(lab[2] + random.randint(-distance, distance), -128, 127)
        return (lab[0], a_new, b_new)
   
    def dim(self, scale):
        brightness_dim = scales.scale_linear(self.brightness_start, self.brightness_end, scale)
        lab_dim = (brightness_dim ** self.gamma, self.lab[1], self.lab[2])
        self.set_color(lab_dim)

    def transition(self, scale):
        a_trans = scales.scale_linear(self.lab_rand[1], self.lab[1], scale)
        b_trans = scales.scale_linear(self.lab_rand[2], self.lab[2], scale)
        self.set_color((self.lab[0], a_trans, b_trans))

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

    def run(self):
        self.lp.lock()
        self.lp.turnOn()
        while(True):
            if not (self.lp.getProfile().strip() == self.lightpack_profile):
                print("wrong profile: " + self.lp.getProfile().strip())
                break
            
            is_between, start_diff, end_diff = self.check_time()

            if is_between:
                if start_diff >= self.dim_duration * 60:
                    self.dim(1)
                    print("sleep for ~" + str(end_diff / 120) + " minutes")
                    sleep(end_diff / 2 + 1)
                else:
                    # dimming process
                    self.dim(start_diff / (self.dim_duration * 60))
                    print("sleep for ~" + str(self.dim_duration / STEPS) + " minutes")
                    sleep((self.dim_duration * 60) / STEPS) # in seconds
            elif self.randomize:
                # transition process
                if start_diff > (self.trans_start * 60):
                    self.transition(0)
                    print("sleep for ~" + str((start_diff - (self.trans_start * 60)) / 120) + " minutes")
                    sleep((start_diff - (self.trans_start * 60)) / 2 + 1)
                else:
                    self.transition(1.0 - start_diff / (self.trans_start * 60))
                    print("sleep for ~" + str(self.trans_start / STEPS) + " minutes")
                    sleep((self.trans_start * 60) / STEPS)
            else:
                self.dim(0)
                print("sleep for ~" + str(start_diff / 120) + " minutes")
                sleep(start_diff / 2 + 1)
        self.lp.unlock()

plugin = DimThis()
sleep(1)
plugin.run()
