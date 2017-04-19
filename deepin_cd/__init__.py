#! /usr/bin/evn python3

import sys

__all__ = ["deepin_cd", "config"]

if sys.version_info[:2] < (3, 5):
    raise Exception('Python version is less than 3.5')
