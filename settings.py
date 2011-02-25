"""User settings

modify this file for your own use
"""
import pymorphous.default_settings
runtime = pymorphous.default_settings.runtime
runtime.init_num_devices = 100
runtime.grid = True
runtime.auto_record = True

WEBOTS_WALL = True

if WEBOTS_WALL:
    target_runtime = 'webots_wall'
else:
    graphics = pymorphous.default_settings.graphics
    #graphics.background_color = (1,1,1,1)
    target_runtime = pymorphous.default_settings.target_runtime
