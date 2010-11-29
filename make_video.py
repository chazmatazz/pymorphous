import ast
import sys
import os
from os.path import splitext
import subprocess

import pymorphous

if len(sys.argv) < 2:
    try:
        import settings
    except ImportError:
        import default_settings as settings
    video_dirs = [float(x) for x in os.listdir(settings.runtime.tmp_dir_video)]
    indir = os.path.join(settings.runtime.tmp_dir_video, str(max(video_dirs)))
else:
    indir = sys.argv[1]
    if not os.path.isdir(indir):
        print "dir to make video not found: %s" % indir
        sys.exit(1)

os.chdir(indir)
asm_proc = subprocess.call("ffmpeg -r 5 -i %d.png video.avi", shell=True)