""" modify this file for your own use """
import default_settings
runtime = default_settings.runtime

WEBOTS = False

if WEBOTS:
    target_runtime = 'webots_wall'
else:
    graphics = default_settings.graphics
    target_runtime = default_settings.target_runtime