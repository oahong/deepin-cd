#! /usr/bin/env python3

import sys
import logging

__all__ = ["deepin_cd"]

logger = logging.getLogger(__name__)

if sys.version_info[:2] < (3, 5):
    raise Exception('Python version is less than 3.5')