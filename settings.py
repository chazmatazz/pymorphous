"""User settings

modify this file for your own use
"""
import pymorphous.default_settings
runtime = pymorphous.default_settings.runtime
runtime.init_num_devices = 15**2
runtime.arrangement = 'tile'
runtime.auto_record = False
runtime.led_wave_wall = False
runtime.graphics_name = 'wall'
    
WEBOTS_WALL = False

if WEBOTS_WALL:
    target_runtime = 'webots_wall'
else:
    graphics = pymorphous.default_settings.graphics
    #graphics.background_color = (1,1,1,1)
    graphics.background = "examples/data/lab.png"
    target_runtime = pymorphous.default_settings.target_runtime
