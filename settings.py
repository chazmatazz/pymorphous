""" modify this file for your own use """
import default_settings
runtime = default_settings.runtime
runtime.init_num_devices = 400
runtime.grid = True
runtime.auto_record = False

WEBOTS_WALL = False

if WEBOTS_WALL:
    target_runtime = 'webots_wall'
else:
    graphics = default_settings.graphics
    #graphics.background_color = (1,1,1,1)
    target_runtime = default_settings.target_runtime
