#!/usr/bin/env python

#
#    Copyright (c) 2010 Brian E. Granger
#
#    This file is part of pyzmq.
#
#    pyzmq is free software; you can redistribute it and/or modify it under
#    the terms of the Lesser GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    pyzmq is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Lesser GNU General Public License for more details.
#
#    You should have received a copy of the Lesser GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os, sys

from distutils.core import setup, Command
from distutils.extension import Extension

from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin, walk


#-----------------------------------------------------------------------------
# Extra commands
#-----------------------------------------------------------------------------

class TestCommand(Command):
    """Custom distutils command to run the test suite."""

    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """Finds all the tests modules in zmq/tests/, and runs them."""
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'zmq', 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['zmq.tests', splitext(basename(t))[0]])
                )
        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)


class CleanCommand(Command):
    """Custom distutils command to clean the .so and .pyc files."""

    user_options = [ ]

    def initialize_options(self):
        self._clean_me = [pjoin('zmq', '_zmq.so'), pjoin('zmq', 'devices.so')]
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.pyc'):
                    self._clean_me.append(pjoin(root, f))

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except:
                pass

#-----------------------------------------------------------------------------
# Extensions
#-----------------------------------------------------------------------------

cmdclass = {'test':TestCommand, 'clean':CleanCommand }

includes = [pjoin('zmq', sub) for sub in ('utils','core','devices')]
# print includes

def pxd(subdir, name):
    return os.path.abspath(pjoin('zmq', subdir, name+'.pxd'))

def pyx(subdir, name):
    return os.path.abspath(pjoin('zmq', subdir, name+'.pyx'))

def dotc(subdir, name):
    return pjoin('zmq', subdir, name+'.c')

czmq = pxd('core', 'czmq')

submodules = dict(
    core = {'constants': [czmq],
            'error':[czmq],
            'poll':[czmq], 
            'stopwatch':[czmq],
            'context':[pxd('core', 'socket'), czmq],
            'message':[czmq],
            'socket':[pxd('core', 'context'), pxd('core', 'message'), czmq],
            'device':[czmq],
            'version':[czmq],
    },
    devices = {
            'basedevice':[pxd('core', 'socket'), pxd('core', 'context'), czmq],
            'monitoredqueue':[pxd('devices', 'base'), czmq],
    },
    utils = {
            'initthreads':[czmq]
    }
)

try:
    from Cython.Distutils import build_ext
except ImportError:
    suffix = '.c'
else:
    suffix = '.pyx'
    cmdclass['build_ext'] =  build_ext

if sys.platform == 'win32':
    libzmq = 'libzmq'
else:
    libzmq = 'zmq'

# init = Extension(
#     'zmq.utils.initthreads',
#     sources = [pjoin('zmq', 'utils', 'initthreads'+suffix)],
#     libraries = [libzmq],
#     include_dirs = includes
# )
extensions = []
for submod, packages in submodules.iteritems():
    for pkg in sorted(packages):
        sources = [pjoin('zmq', submod, pkg+suffix)]
        if suffix == '.pyx':
            sources.extend(packages[pkg])
        ext = Extension(
            'zmq.%s.%s'%(submod, pkg),
            sources = sources,
            libraries = [libzmq],
            include_dirs = includes
        )
        extensions.append(ext)
        
#-----------------------------------------------------------------------------
# Main setup
#-----------------------------------------------------------------------------

long_desc = \
"""
PyZMQ is a lightweight and super-fast messaging library built on top of
the ZeroMQ library (http://www.zeromq.org). 
"""

setup(
    name = "pyzmq",
    version = "2.0.9dev",
    packages = ['zmq', 'zmq.tests', 'zmq.eventloop', 'zmq.log', 'zmq.core', 'zmq.devices'],
    ext_modules = extensions,
    package_data = {'zmq':['*.pxd'],
                    'zmq.core':['*.pxd'],
                    'zmq.devices':['*.pxd'],
    },
    author = "Brian E. Granger",
    author_email = "ellisonbg@gmail.com",
    url = 'http://github.com/zeromq/pyzmq',
    download_url = 'http://github.com/zeromq/pyzmq/downloads',
    description = "Python bindings for 0MQ.",
    long_description = long_desc, 
    license = "LGPL",
    cmdclass = cmdclass,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: System :: Networking'
    ]
)

