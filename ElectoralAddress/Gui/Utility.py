
from functools import wraps
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

def HandleException(title ):
    title = title if title else "Error"
    message = str(sys.exc_info()[1])
    QMessageBox.warning(None,title,message)

def attempt( title=None, default=None ):
    if callable(title) and default == None:
        f = title
        title = "Error in " + f.__name__
        @wraps(f)
        def wrapper( *args, **kwds):
            try:
                return f(*args, **kwds)
            except:
                HandleException(title)
            return None
        return wrapper
    def handler(f):
        htitle = title if title else "Error in "+f.__name__
        @wraps(f)
        def wrapper(*args, **kwds ):
            try:
                return f( *args, **kwds)
            except:
                HandleException(title)
            return default
        return wrapper
    return handler
