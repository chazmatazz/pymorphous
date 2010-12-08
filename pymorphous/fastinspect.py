import sys
import types
import inspect
from collections import namedtuple

FastTraceback = namedtuple('FastTraceback', 'filename lineno')

def getframeinfo(frame):
    """Get information about a frame or traceback object.

    A tuple of five things is returned: the filename, the line number of
    the current line, the function name, a list of lines of context from
    the source code, and the index of the current line within that list.
    The optional second argument specifies the number of lines of context
    to return, which are centered around the current line."""
    if inspect.istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    else:
        lineno = frame.f_lineno
    if not inspect.isframe(frame):
        raise TypeError('arg is not a frame or traceback object')

    return FastTraceback(frame.f_code.co_filename, lineno)

def stack(stop):
    """Return a list of records for the stack above the caller's frame until stop"""
    frame = sys._getframe(2)
    frame_info = getframeinfo(frame)
    stop_info = getframeinfo(stop)
    framelist = []
    #while (frame 
    #       and not (frame_info.filename == stop_info.filename
    #       and frame_info.lineno == stop_info.lineno)):
    while frame:
        framelist += [(frame,) + frame_info]
        frame = frame.f_back
        if frame:
            frame_info = getframeinfo(frame)
    return framelist

