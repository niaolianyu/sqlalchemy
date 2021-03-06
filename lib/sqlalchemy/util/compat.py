# util/compat.py
# Copyright (C) 2005-2013 the SQLAlchemy authors and contributors <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Handle Python version/platform incompatibilities."""

import sys

try:
    import threading
except ImportError:
    import dummy_threading as threading

py33 = sys.version_info >= (3, 3)
py32 = sys.version_info >= (3, 2)
py3k = sys.version_info >= (3, 0)
py2k = sys.version_info < (3, 0)
jython = sys.platform.startswith('java')
pypy = hasattr(sys, 'pypy_version_info')
win32 = sys.platform.startswith('win')
cpython = not pypy and not jython  # TODO: something better for this ?

import collections
next = next

if py3k:
    import pickle
else:
    try:
        import cPickle as pickle
    except ImportError:
        import pickle

ArgSpec = collections.namedtuple("ArgSpec",
                ["args", "varargs", "keywords", "defaults"])

if py3k:
    import builtins

    from inspect import getfullargspec as inspect_getfullargspec
    from urllib.parse import quote_plus, unquote_plus, parse_qsl
    import configparser
    from io import StringIO

    from io import BytesIO as byte_buffer

    def inspect_getargspec(func):
        return ArgSpec(
                    *inspect_getfullargspec(func)[0:4]
                )

    string_types = str,
    binary_type = bytes
    text_type = str
    int_types = int,
    iterbytes = iter

    def u(s):
        return s

    def ue(s):
        return s

    def b(s):
        return s.encode("latin-1")

    if py32:
        callable = callable
    else:
        def callable(fn):
            return hasattr(fn, '__call__')

    def cmp(a, b):
        return (a > b) - (a < b)

    from functools import reduce

    print_ = getattr(builtins, "print")

    import_ = getattr(builtins, '__import__')

    import itertools
    itertools_filterfalse = itertools.filterfalse
    itertools_filter = filter
    itertools_imap = map

    import base64
    def b64encode(x):
        return base64.b64encode(x).decode('ascii')
    def b64decode(x):
        return base64.b64decode(x.encode('ascii'))

else:
    from inspect import getargspec as inspect_getfullargspec
    inspect_getargspec = inspect_getfullargspec
    from urllib import quote_plus, unquote_plus
    from urlparse import parse_qsl
    import ConfigParser as configparser
    from StringIO import StringIO
    from cStringIO import StringIO as byte_buffer

    string_types = basestring,
    binary_type = str
    text_type = unicode
    int_types = int, long
    def iterbytes(buf):
        return (ord(byte) for byte in buf)

    def u(s):
        # this differs from what six does, which doesn't support non-ASCII
        # strings - we only use u() with
        # literal source strings, and all our source files with non-ascii
        # in them (all are tests) are utf-8 encoded.
        return unicode(s, "utf-8")

    def ue(s):
        return unicode(s, "unicode_escape")

    def b(s):
        return s

    def import_(*args):
        if len(args) == 4:
            args = args[0:3] + ([str(arg) for arg in args[3]],)
        return __import__(*args)

    callable = callable
    cmp = cmp
    reduce = reduce

    import base64
    b64encode = base64.b64encode
    b64decode = base64.b64decode

    def print_(*args, **kwargs):
        fp = kwargs.pop("file", sys.stdout)
        if fp is None:
            return
        for arg in enumerate(args):
            if not isinstance(arg, basestring):
                arg = str(arg)
            fp.write(arg)

    import itertools
    itertools_filterfalse = itertools.ifilterfalse
    itertools_filter = itertools.ifilter
    itertools_imap = itertools.imap


import time
if win32 or jython:
    time_func = time.clock
else:
    time_func = time.time

from collections import namedtuple
from operator import attrgetter as dottedgetter


if py3k:
    def reraise(tp, value, tb=None, cause=None):
        if cause is not None:
            value.__cause__ = cause
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    def raise_from_cause(exception, exc_info=None):
        if exc_info is None:
            exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        reraise(type(exception), exception, tb=exc_tb, cause=exc_value)
else:
    exec("def reraise(tp, value, tb=None, cause=None):\n"
            "    raise tp, value, tb\n")

    def raise_from_cause(exception, exc_info=None):
        # not as nice as that of Py3K, but at least preserves
        # the code line where the issue occurred
        if exc_info is None:
            exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        reraise(type(exception), exception, tb=exc_tb)

if py3k:
    exec_ = getattr(builtins, 'exec')
else:
    def exec_(func_text, globals_, lcl=None):
        if lcl is None:
            exec('exec func_text in globals_')
        else:
            exec('exec func_text in globals_, lcl')


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass.

    Drops the middle class upon creation.

    Source: http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/

    """

    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


