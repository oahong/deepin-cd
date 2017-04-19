#! /usr/bin/env python3

import os
import argparse
import logging
import pprint

from deepin_cd.deepin_cd import DeepinCD
from deepin_cd.config import __VERSION__, __ARCHS__

if __name__ == '__main__':
    #TODO: preseed not implemented
    parser = argparse.ArgumentParser(
        description='Build a custom installation media for deepin server.')
    parser.add_argument('--preseed', '-s',
                        help='Include the preseed in installation media')
    parser.add_argument('--arch', '-a', default='mips64el',
                        choices=__ARCHS__, help='Specify target architecture')
    parser.add_argument('--include-package', '-i', nargs='*', default=[''],
                        help='Add additional package to installation media')
    parser.add_argument('--exclude-package', '-e', nargs='*', default=[''],
                        help='Exclude the package from installation media')
    parser.add_argument('--log-level', '-l', choices=['debug', 'info'],
                        default='info', help='Set logging level')
    parser.add_argument('--workdir', '-w', default='/work/debian-cd',
                        help='Project workdir, debian-cd resides in this place')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __VERSION__)
    options = parser.parse_args()

    logging.basicConfig(level=getattr(logging, options.log_level.upper()))
    logger = logging.getLogger(__name__)
    logger.info('program started: %s, version: %s' % (parser.prog, __VERSION__))
    
    """
    make a deepin cd in following steps:
    1. Add arch (mips64el in this case) specific boot files
    2. Append a list of packages to deepin-extra task file
    3. Append a list of packages to exclude, which will be exclude from debian-cd explicitly
    4. execute easy-build.sh, options can be specified by using environment variables
    5. Print the final ISO image
    """
    workDir = options.workdir
    taskDir = os.path.join(options.workdir, 'tasks', DeepinCD.codename)

    cd = DeepinCD(options.arch, '15.2', 23, workDir)
    cd.initialize_workdir()

    cd.append_package_list(options.include_package,
                               os.path.join(taskDir, 'deepin-extra'))
    cd.append_package_list(options.exclude_package,
                               os.path.join(taskDir, 'exclude'))
    cd.add_boot_files('/work/loongson-boot', options.preseed)

    # make a new installation disc image
    cd.make_disc()
    logger.info("programme finished")
