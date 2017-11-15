#! /usr/bin/evn python

import os
import shutil

from deepin_cd.config import __ARCHS__
from deepin_cd.utils import runcmd
from datetime import date

import logging

logger = logging.getLogger(__name__)

class DebianCD(object):
    """
    Set environment and run easy-build.sh to build
    a complete installation media
    """
    codename = 'kui'
    debian_cd_url = 'http://git.sh.sndu.cn/hhao/debian-cd'

    def __init__(
            self, arch, version, build_id, work,
            output, repo, project='deepin'):
        """
        project is a custom cd identifier or project name
        """
        self.arch = arch
        self.version = version
        self.build_id = build_id
        self.project = project

        self.work = work
        self.output = output
        self.mirror = repo

        self.target_cd = '{}-{}-{}-B{}-DVD-1.iso'.format(
            self.project, self.version, self.arch, self.build_id)
        logger.info('Target media is {} lives in {}'.format(
            self.target_cd, self.output))

    @property
    def arch(self):
        return self._arch

    @arch.setter
    def arch(self, value):
        if value in __ARCHS__:
            self._arch = value
        else:
            e = ValueError('{} is not a supported architecture'.format(value))
            logger.exception(e)
            raise(e)

    @property
    def build_id(self):
        return self._build_id

    @build_id.setter
    def build_id(self, value):
        try:
            self._build_id = int(value)
        except ValueError as e:
            logger.exception(e)
            raise(e)

    def __get_output_dir(self):
        return os.path.join(
            self.output, self.version, str(date.today()))

    def get_artifact(self):
        """
        validate the final image
        """
        artifact = os.path.join(self.__get_output_dir(),
                                self.target_cd)
        if os.path.exists(artifact):
            return artifact
        else:
            raise FileNotFoundError('{} not found'.format(artifact))

    def initialize_work(self):
        os.makedirs(self.work, exist_ok=True)
        if not os.listdir(self.work):
            logger.info('fetching debian-cd source code into {}'.format(
                self.work))
            runcmd(['git', 'clone', DebianCD.debian_cd_url, self.work], cwd=self.work)
        else:
            logger.info('update debian-cd source code')
            runcmd(['git', 'pull'], cwd=self.work)

    def make_disc(self):
        """
        A debian-cd wrapper.
        """
        logger.info("Start to build ISO image")
        runcmd(['bash', 'easy-build.sh', '-d', 'light', 'BC', self.arch], cwd=self.work)


class DeepinCD(DebianCD):
    @staticmethod
    def append_package_list(package_list, taskfile):
        """
        write package list or copy package list file to a task file,
        this file is predefined in debian-cd
        """
        logger.debug("package list: %s will append to %s", package_list, taskfile)
        if os.path.isfile(package_list):
            shutil.copy(package_list, taskfile)
            logger.debug("copy %s to %s", package_list, taskfile)
        else:
            logger.debug("append %s to %s", package_list, taskfile)
            with open(taskfile, 'w') as f:
                f.write('\n'.join(package_list))

    @staticmethod
    def add_late_command(script):
        raise NotImplementedError

    @staticmethod
    def add_boot_files(bootdir):
        if os.path.exists(bootdir):
            # TODO: fix debian-cd, copy boot files from a path
            # set by environment variable
            pass
        else:
            pass

    def make_disc(self):
        """
        To finish the make_disc operation, debian-cd should:
        - follow debian upstream as much as possible, don't make unnessisary modifications to scripts
        - copy boot specific files (or ISO skeleton) from a central place, different projects share
          same copy of ISO skeleton
        - project specific modification, besides exta debian-cd tasks, comes from project configuratoin
        - write artifacts to output dir, which is set via configuration
        """
        logger.info("Start to build ISO image for %s", self.arch)
        runcmd(['bash', 'deepin-build.sh', 'DVD', self.arch],
                    env={'PROJECT': self.project,
                         'CDVERSION': self.version,
                         'WORK': self.work,
                         'OUTPUT': self.output,
                         'BUILD_ID': str(self.build_id),
                         'DEEPIN_MIRROR': self.mirror
                    },
                    cwd=self.work
        )

if __name__ == '__main__':
    cd = DeepinCD('mips64el', '14.3', 23,
                  '/work/debian-cd', '/work/output', '/work/mirrors/mips64el')
    cd.make_disc()
    cd.get_artifact()
