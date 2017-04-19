#! /usr/bin/evn python

import os
import re
import logging
import shutil

from datetime import date
try:
    from subprocess import DEVNULL, PIPE, run
except:
    raise Exception("Require python version >= 3.5")

logger = logging.getLogger(__name__)


class DebianCD(object):
    """
    Set environment and run easy-build.sh to build
    a complete installation media
    """
    codename = 'kui'
    debian_cd_url = 'http://git.sh.sndu.cn/hhao/debian-cd'
    id_file = 'CURRENT_BUILD_ID'

    def __init__(self, arch, version, build_id, workdir, name='deepin'):
        """
        name is a custom cd name, in most cases it's deepin
        """
        self.arch = arch
        self.version = version
        self.build_id = build_id
        self.name = name
        self.workdir = workdir

        self.target_cd = '{}-{}-{}-B{}-DVD-1.iso'.format(
            self.name, version, arch, build_id)
        logger.info('Target media is {}'.format(self.target_cd))

    def get_output_dir(self):
        return os.path.join(self.workdir, 'output', self.version)

    def get_build_id(self):
        with open(os.path.join(
                self.get_output_dir(), self.id_file), 'r') as f:
            build_id = f.readline().strip()

        if build_id.isdigit():
            return int(build_id)+1
        else:
            return 1

    def set_build_id(self, id):
        if type(id) == int:
            id += 1
        else:
            raise ValueError("id: {} is invalid".format(id))
        with open(os.path.join(
                self.get_output_dir(), self.id_file), 'w') as f:
            f.write('\n'.join(id))

    def get_artifact(self):
        """
        validate the final image
        """
        artifact = os.path.join(self.get_output_dir(),
                                str(date.today()),
                                self.target_cd)
        if os.path.exists(artifact):
            return artifact
        else:
            raise IOError('{} not found'.format(artifact))

    def initialize_workdir(self):
        os.makedirs(self.workdir, exist_ok=True)
        if not os.listdir(self.workdir):
            logger.info('fetching debian-cd source code into {}'.format(
                self.workdir))
            self.runcmd(['git', 'clone', DebianCD.debian_cd_url, self.workdir])

    @staticmethod
    def runcmd(cmd, env={}):
        """
        Run cmd with env, check return code then print stdout
        """
        logger.debug('runcmd %s with env %s', cmd, env)
        if env:
            cp = run(cmd, stdout=PIPE, check=True, env=env)
        else:
            cp = run(cmd, stdout=PIPE, check=True)
        print(cp.stdout.decode())

    @staticmethod
    def append_package_list(packageList, taskFile):
        """
        write package list to a task file, this file is predefined in debian-cd
        """
        if os.path.isfile(packageList):
            shutil.copy(packageList, taskFile)
        with open(taskFile, 'w') as f:
            f.write('\n'.join(packageList))

    @staticmethod
    def add_late_command(script):
        raise NotImplementedError

    @staticmethod
    def add_boot_files(bootPath, preseed):
        if os.path.exists(bootPath):
            # TODO: fix debian-cd, copy boot files from a path
            # set by environment variable
            pass
        else:
            pass

    def make_disc(self):
        """
        A debian-cd wrapper.
        """
        os.chdir(self.workdir)
        logger.info("Start to build ISO image")
        self.runcmd(['bash', 'easy-build.sh', '-d', 'light', 'BC', self.arch])
        self.get_artifact()


class LiveBootCD(object):
    """
    Another class for live-boot based installation media,
    which is used in sw64(alpha) platform right now
    """
    pass


class DeepinCD(DebianCD):
    def make_disc(self):
        logger.info("Start to build ISO image for %s", self.arch)
        os.chdir(os.path.join(self.workdir, 'deepin', self.codename))
        self.runcmd(['bash', '/tmp/build-cd1.sh'], env={'TEST': 'ABC'})


if __name__ == '__main__':
    cd = DeepinCD('mips64el', '2014.3', 23, '/tmp')
    cd.make_disc()
    cd.get_artifact()
