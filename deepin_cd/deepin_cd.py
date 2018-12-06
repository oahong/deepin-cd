#! /usr/bin/python3

import logging
import argparse
import os.path as osp

from datetime import date
from pprint import pformat

from deepin_cd.profile import BuildProfile
from deepin_cd.debian_cd import DebianCDRepo
from deepin_cd.utils import log_and_raise_exception, runcmd
from deepin_cd.config import __architectures__, __version__

logger = logging.getLogger(__name__)


class DeepinCD():

    def __init__(self):
        args = vars(self.read_cli_args()).items()
        self.args = { k: v for k, v in args if v }
        logger.info('Script arguments:\n{}'.format(
            pformat(self.args, indent=4)))

        if 'config' in self.args:
            profile = BuildProfile(self.args['config']).get_profile()
            # PEP448, merge command line arguments and configurations,
            # arguments have higher priorities than configurations
            self.profile = { **profile, **self.args }
        else:
            self.profile = BuildProfile(self.args).get_profile()

        logger.info('Build profile:\n{}'.format(
            pformat(self.profile, indent=4)))

    def read_cli_args(self):
        """
        Read command line arguments, return command line arguments as a set
        """
        parser = argparse.ArgumentParser(
        description='An installation media generator for deepin server.')
        optgroup = parser.add_argument_group('Build option arguments')
        optgroup.add_argument('--arch', '-a', choices=__architectures__,
            help='Specify target architecture, mips64el is default')
        optgroup.add_argument('--build', '-b', type=int, help='Set build ID')
        optgroup.add_argument('--output', '-o',
            help='Output dir in which the final artifacts live')
        optgroup.add_argument('--repository', '-r',
            help='Specify the local location of package repository')
        optgroup.add_argument('--skeleton', '-s', help='ISO skeleton dir')
        optgroup.add_argument('--work', '-w',
            help='Project work dir, debian-cd resides in this place')
        optgroup.add_argument('--project', '-p', help='Set procject name')

        cfggroup = parser.add_argument_group('Configuration file arguments')
        cfggroup.add_argument('--config', '-c', help="load configuration file")

        parser.add_argument('--version', '-v', action='version',
            version='%(prog)s ' + __version__)
        return parser.parse_args()

    def _get_output_dir(self):
        return osp.join(
            self.profile['output'],
            self.profile['version'],
            str(date.today()))

    def _get_image(self):
        return '{}-{}-B{}-{}-DVD-1.iso'.format(
            self.profile['project'], self.profile['version'],
            self.profile['build'], self.profile['arch'])

    def get_artifact(self):
        """
        validate the final image
        """
        artifact = osp.join(self._get_output_dir(), self._get_image())
        if osp.exists(artifact):
            return artifact
        else:
            raise FileNotFoundError('{} not found'.format(artifact))

    def build_image(self):
        # branch name pattern: arch-project (sw_64-10P)
        branch = "{}-{}".format(self.profile['arch'],
            self.profile['project'].lstrip('deepin-server'))
        logger.info("Fetching debian-cd source code on branch {}" % branch)

        repo = DebianCDRepo(self.profile['work'], branch)
        repo.fetch_src()

        logger.info("Start to build installation image")
        cmdenv = {
            'PROJECT': self.profile['project'],
            'CDVERSION': self.profile['version'],
            'WORK': self.profile['work'],
            'OUTPUT': self.profile['output'],
            # fallback to a special 0 build_id, indicates a test build
            'BUILD_ID': str(self.profile.get('build', 0)),
            'DEEPIN_MIRROR': self.profile['repository'],
        }
        if 'skeleton' in self.profile:
            cmdenv['ISO_SKELETON'] = self.profile['skeleton']

        runcmd(['bash', 'deepin-build.sh', 'DVD', self.profile['arch']],
               env=cmdenv,
               cwd=self.profile['work'])


if __name__ == '__main__':
    cd = DeepinCD()
    cd.build_image()
    cd.get_artifact()
