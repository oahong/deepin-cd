#! /usr/bin/env python3

import os
import argparse
import logging
import json
import pprint

from deepin_cd.deepin_cd import DeepinCD
from deepin_cd.config import __VERSION__, __ARCHS__

def set_value(x, y, allow_empty = True):
    result = x or y
    if result or allow_empty:
        return result
    else:
        raise ValueError("both values are invalid")

if __name__ == '__main__':
    #TODO: preseed not implemented
    parser = argparse.ArgumentParser(
        description='A custom installation media generator for deepin server.')
    optgroup = parser.add_argument_group('Build option arguments')
    optgroup.add_argument('--preseed', '-s', default='deepin.preseed',
                        help='use the preseed in installation media')
    optgroup.add_argument('--arch', '-a', default='mips64el',
                        choices=__ARCHS__, help='Specify target architecture, mips64el is default')
    optgroup.add_argument('--build-id', '-b', type=int, help='Set build ID')
    optgroup.add_argument('--include', '-i', nargs='*', default=[],
                        help='Add additional packages to installation media')
    optgroup.add_argument('--exclude', '-e', nargs='*', default=[],
                        help='Exclude packages from installation media')
    parser.add_argument('--workdir', '-w', default='/work/debian-cd',
                        help='Project workdir, debian-cd resides in this place')
    cfggroup = parser.add_argument_group('Configuration file arguments')
    cfggroup.add_argument('--config', '-c', help="load configuration from a json file")
    parser.add_argument('--log-level', '-l', choices=['debug', 'info'],
                        default='info', help='Set logging level')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __VERSION__)
    options = parser.parse_args()

    logging.basicConfig(level=getattr(logging, options.log_level.upper()))
    logger = logging.getLogger(__name__)
    logger.info('program started: %s, version: %s' % (parser.prog, __VERSION__))

    """
    make a deepin cd in 5 steps:
    1. Add arch (mips64el in this case) specific boot files (hard-coded in debian-cd currently)
    2. Append a list of packages to deepin-extra task file
    3. Append a list of packages to exclude, which will be exclude from debian-cd explicitly
    4. execute easy-build.sh, options can be specified by using environment variables
    5. Print the final ISO image
    """
    workDir = options.workdir
    taskDir = os.path.join(options.workdir, 'tasks', DeepinCD.codename)

    configs = {}

    if options.config:
        # options has been specified via json config
        with open(options.config, 'r') as f:
            configs = json.load(f)
        pprint.pprint(configs)
    else:
        configs = {
            'arch': '', 'include': '', 'exclude': '',
            'name': '', 'preseed': '', 'task': ''
        }

    arch = set_value(configs['arch'], options.arch, allow_empty=False)
    build_id = set_value(configs['task'], options.build_id, allow_empty=False)
    name_version = set_value(configs['name'], 'deepin-15.1')
    name = ''.join(name_version.split('-')[:2])
    version = name_version.split('-')[-1]

    exclude = set_value(configs['exclude'], options.exclude)
    include = set_value(configs['include'], options.include)
    preseed = set_value(configs['preseed'], options.preseed)

    cd = DeepinCD(arch, version, build_id, workDir)
    cd.initialize_workdir()

    #cd.add_boot_files('/work/loongson-boot')
    cd.append_package_list(include,
                           os.path.join(taskDir, 'deepin-extra'))
    cd.append_package_list(exclude,
                           os.path.join(taskDir, 'exclude'))

    cd.make_disc()
    logger.info("programme finished")
