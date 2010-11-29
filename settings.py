""" modify this file for your own use """
import default_settings
runtime = default_settings.runtime
runtime.init_num_devices = 1600
runtime.grid = True
runtime.auto_record = True

WEBOTS = False

if WEBOTS:
    target_runtime = 'webots_wall'
else:
    graphics = default_settings.graphics
    target_runtime = default_settings.target_runtime