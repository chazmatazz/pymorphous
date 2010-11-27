import pymorphous.simulator_constants

class _Runtime(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
        self['init_num_devices'] = 1000
        self['steps_per_frame'] = 1
        self['desired_fps'] = 50
        self['dim'] = [132,100,0]
        self['body_rad'] = None
        self['radio_range'] = 15
        self['window_width'] = 1000
        self['window_height'] = 1000
        self['window_title'] = None
        self['_3D'] = False
        self['headless'] = False
        self['show_leds'] = True
        self['led_flat'] = False
        self['led_stacking_mode'] = pymorphous.simulator_constants.LED_STACKING_MODE_DIRECT
        self['show_body'] = True
        self['show_radio'] = False
        self['grid'] = False
        self['use_graphics'] = pymorphous.constants.UNSPECIFIED
        
    def __getattr__(self, name):
        return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value

runtime = _Runtime()

class _Graphics(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
        self['background'] = (0, 0, 0, 0)
        self['simple_body'] = (1, 0.25, 0, 0.8)
        self['selected_device'] = (1,1,1,0.2)
        self['radio_range_ring'] = (0.25, 0.25, 0.25, 0.8)
        self['user_sensor_0'] = (1, 0.5, 0, 0.8)
        self['user_sensor_1'] = (0.5, 0, 1, 0.8)
        self['user_sensor_2'] = (1, 0, 0.5, 0.8)
        self['red_led'] = (1, 0, 0, 0.8)
        self['green_led'] = (0, 1, 0, 0.8)
        self['blue_led'] = (0, 0, 1, 0.8)
    
    def __getattr__(self, name):
        return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value
    
    @property
    def _user_sensors(self):
        return [self.user_sensor_0, self.user_sensor_1, self.user_sensor_2]
    
    @property
    def _leds(self):
        return [self.red_led, self.green_led, self.blue_led]

graphics = _Graphics()

target_runtime = 'simulator'