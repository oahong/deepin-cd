#! /usr/bin/env python3

import os
import argparse
import logging
import json
import pprint

from deepin_cd.deepin_cd import DeepinCD
from deepin_cd.config import __VERSION__, __ARCHS__
from deepin_cd.utils import set_value

def parse_opts():
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
    parser.add_argument('--work', '-w', default='/work/debian-cd',
                        help='Project work dir, debian-cd resides in this place')
    parser.add_argument('--output', '-o',
                            help='Output dir in which the final artifacts live')
    cfggroup = parser.add_argument_group('Configuration file arguments')
    cfggroup.add_argument('--config', '-c', help="load configuration from a json file")
    parser.add_argument('--log-level', '-l', choices=['debug', 'info'],
                        default='info', help='Set logging level')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __VERSION__)

    return parser.parse_args()

def main(options):
    """
    Make a deepin cd in 5 steps:
    1. Add arch (mips64el/sw64) specific boot files (hard-coded in debian-cd at the time of writing)
    2. Append a list of packages to deepin-extra task file
    3. Append a list of packages to exclude, which will be exclude from debian-cd explicitly
    4. execute easy-build.sh, opts can be specified by using environment variables
    5. Print the final build artifacts
    """
    logging.basicConfig(level=getattr(logging, opts.log_level.upper()))
    logger = logging.getLogger(__name__)
    logger.info('program started version: %s' % __VERSION__)

    if opts.config:
        # opts has been specified via json config
        logger.info("load configuration from %s", opts.config)
        with open(opts.config, 'r') as f:            configs = json.load(f)

        config_dir = os.path.realpath(os.path.dirname(opts.config))
        logger.debug("dump configurations in {}:\n {}".format(
            config_dir, pprint.pformat(configs, 4)))
    else:
        configs = {
            'arch': '', 'include': '', 'exclude': '',
            'name': '', 'preseed': '', 'task': '',
            'workbase': '', 'output': '', 'repo': '',
        }

    arch = set_value(configs['arch'], opts.arch, allow_empty=False)
    build_id = set_value(configs['task'], opts.build_id, allow_empty=False)

    # fall back to deepin-server-15.1
    name = set_value(configs['name'], 'deepin-server')
    version = set_value(configs['tag'], '15.1')

    exclude = set_value(configs['exclude'], opts.exclude)
    include = set_value(configs['include'], opts.include)
    preseed = set_value(configs['preseed'], opts.preseed)
    output  = set_value(configs['output'], opts.output)
    work = set_value(configs['workbase'], opts.work)

    cd = DeepinCD(arch, version, build_id, work, output)
    cd.initialize_work()

    #cd.add_boot_files('/work/loongson-boot')
    task_dir = os.path.join(opts.work, 'tasks', DeepinCD.codename)
    cd.append_package_list(os.path.join(config_dir, include),
                           os.path.join(task_dir, 'deepin-extra'))
    cd.append_package_list(os.path.join(config_dir, exclude),
                           os.path.join(task_dir, 'exclude'))

    cd.make_disc()
    logger.info("programme finished")

if __name__ == '__main__':
    opts = parse_opts()
    main(opts)
