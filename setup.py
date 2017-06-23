import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "deepin CD image generator",
    version = "0.2",
    author = "Hong Hao",
    author_email = "honghao@deepin.com",
    description = ("A wrapper script around debian-cd"
                   "to build custom deepin installation media."),
    license = "GPL-2",
    keywords = "deepin CD customization",
    url = "https://github.com/oahong/deepin-cd",
    packages=['deepin_cd'],
    scripts=['test_deepin_cd.py'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
)
