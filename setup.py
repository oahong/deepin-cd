import os.path as osp
from setuptools import setup, find_packages
from deepin_cd.config import __version__, __author__, __email__, __license__


def read(fname):
    with open(osp.join(osp.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name="deepin CD image generator",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=("A wrapper script around debian-cd"
                 "to build custom deepin installation media"),
    license=__license__,
    keywords="deepin CD customization",
    url="https://github.com/oahong/deepin-cd",
    install_requires=read('requirements.txt').strip().split('\n'),
    packages=find_packages(),
    scripts=['deepin-cd'],
    data_files=[('config', ['config/config.json'])],
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