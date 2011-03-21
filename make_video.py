# Copyright (C) 2011 by Charles Dietrich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import os
import subprocess

if len(sys.argv) < 2:
    try:
        import settings
    except ImportError:
        import pymorphous.default_settings as settings
    video_dirs = [float(x) for x in os.listdir(settings.runtime.tmp_dir_video)]
    indir = os.path.join(settings.runtime.tmp_dir_video, str(max(video_dirs)))
else:
    indir = sys.argv[1]
    if not os.path.isdir(indir):
        print "dir to make video not found: %s" % indir
        sys.exit(1)

print indir
os.chdir(indir)
asm_proc = subprocess.call("ffmpeg -r 20 -i %d.png video.avi", shell=True)