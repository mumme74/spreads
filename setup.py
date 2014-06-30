#!/usr/bin/env python2.7
import os
from subprocess import check_call
from setuptools import setup
from setuptools.command.sdist import sdist as SdistCommand

import spreads

if os.path.exists('README.rst'):
    description_long = open('README.rst').read()
else:
    description_long = """
spreads is a tool that aims to streamline your book scanning workflow.  It
takes care of every step=Setting up your capturing devices, handling the
capturing process, downloading the images to your machine, post-processing them
and finally assembling a variety of output formats.

Along the way you can always fine-tune the auto-generated results either by
supplying arguments or changing the configuration beforehand, or by inspecting
the output and applying your modifications.

It is meant to be fully customizable. This means, adding support for new
devices is made as painless as possible. You can also hook into any of the
commands by implementing one of the available plugin hooks or even implement
your own custom sub-commands.
"""


class CustomSdistCommand(SdistCommand):
    def run(self):
        check_call(['make', '-C', 'spreadsplug/web/client', 'production'])
        SdistCommand.run(self)

setup(
    name="spreads",
    version=spreads.__version__,
    author="Johannes Baiter",
    author_email="johannes.baiter@gmail.com",
    url="http://spreads.readthedocs.org",
    description="Book digitization workflow suite",
    long_description=description_long,
    license="GNU AGPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Graphics :: Capture",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    keywords=[
        "digitization",
        "scanning",
        "chdk",
        "diybookscanner",
        "bookscanning",
    ],
    packages=[
        "spreads",
        "spreads.vendor",
        "spreads.vendor.huey",
        "spreads.vendor.huey.backends",
        "spreadsplug",
        "spreadsplug.dev",
        "spreadsplug.gui",
        "spreadsplug.web",
    ],
    scripts=[
        "spread"
    ],
    package_data={
        'spreadsplug.gui': ['pixmaps/monk.png'],
        'spreadsplug.web': ['client/index.html', 'client/build/*']
    },
    entry_points={
        'spreadsplug.devices': [
            "chdkcamera=spreadsplug.dev.chdkcamera:CHDKCameraDevice",
            "gphoto2camera=spreadsplug.dev.gphoto2camera:GPhoto2CameraDevice",
        ],
        'spreadsplug.hooks': [
            "autorotate     =spreadsplug.autorotate:AutoRotatePlugin",
            "scantailor     =spreadsplug.scantailor:ScanTailorPlugin",
            "pdfbeads       =spreadsplug.pdfbeads:PDFBeadsPlugin",
            "djvubind       =spreadsplug.djvubind:DjvuBindPlugin",
            "tesseract      =spreadsplug.tesseract:TesseractPlugin",
            "gui            =spreadsplug.gui:GuiCommand",
            "web            =spreadsplug.web:WebCommands",
            "intervaltrigger=spreadsplug.intervaltrigger:IntervalTrigger",
            "hidtrigger     =spreadsplug.hidtrigger:HidTrigger",
        ]
    },
    install_requires=[
        "colorama >= 0.2.4",
        "PyYAML >= 3.10",
        "futures >= 2.1",
        "blinker >= 1.3",
        "roman >= 2.0.0",
    ],
    extras_require={
        "chdkcamera": ["pyusb >= 1.0.0b1", "jpegtran-cffi >= 0.4"],
        "gphoto2camera": ["piggyphoto >= 0.1"],
        "autorotate": ["jpegtran-cffi >= 0.4"],
        "gui": ["PySide >= 1.2.1"],
        "hidtrigger": ["hidapi-cffi >= 0.1"],
        "scantailor": ["psutil==2.1.1"],
        "web": [
            "Flask >= 0.10.1",
            "jpegtran-cffi >= 0.4",
            "requests >= 2.2.0",
            "waitress >= 0.8.8",
            "zipstream >= 1.0.2",
            "tornado >= 3.1",
            "Wand >= 0.3.5",
        ]
    },
    cmdclass={'sdist': CustomSdistCommand}
)
