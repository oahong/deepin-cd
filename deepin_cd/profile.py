#! /usr/bin/python3

import logging
import json
import re
import os.path as osp

from deepin_cd.config import __architectures__
from deepin_cd.utils import log_and_raise_exception, get_native_arch

logger = logging.getLogger(__name__)


class BuildProfile:

    def __init__(self, conf):
        """
        load build profile from a dict or configuration file
        """
        if isinstance(conf, dict):
            self.profile = conf
        elif osp.isfile(conf):
            self.profile = self.read_config(conf)
        self.validate_profile()

    def get_profile(self):
        """ Validate and return the build profile """
        return self.profile

    def read_config(self, conf):
        """
        Load a build profile from json config
        """
        with open(conf) as f:
            config = json.load(f)
            logger.debug("configuration contents is:\n{}".format(
                json.dumps(config, indent=4)))
        return config

    def validate_profile(self):
        """
        validate a build profile, raise an exception if
        profile is invalid
        """
        # to make a build we must have those keys in the profile
        must_have_keys={
            'version', 'output', 'repository', 'skeleton',  'work'
        }
        if must_have_keys.issubset(self.profile):
            self.__check_path_spec()
            self.__check_version()
            self.__check_target_arch()
            self.__check_build_id()
        else:
            e = AttributeError("Incomplete build profile {}, must have at least {}".format(
                self.profile, must_have_keys))
            log_and_raise_exception(e)

    def __check_path_spec(self):
        path_specs = ( 'output', 'repository', 'skeleton',  'work' )
        # validating path spec in the build profile
        for key in path_specs:
            path = self.profile[key]
            try:
                osp.isdir(path)
                logger.debug("{} is a valid path spec".format(path))
            except (TypeError, NotADirectoryError) as e:
                log_and_raise_exception(
                    ValueError("Invalid path spec {}".format(path)))

    def __check_version(self):
        version = self.profile['version']
        pattern = '^\d+\.\d+$'

        if not re.match(pattern, version):
            log_and_raise_exception(
                ValueError("Version {} pattern is invalid").format(version))

    def __check_target_arch(self):
        """
        target arch must in __architectures__
        Use host arch if we can not load arch from configuration
        """
        if 'arch' not in self.profile:
            # arch not defined, return host arch
            self.profile['arch'] = get_native_arch()
        if self.profile['arch'] not in __architectures__:
            log_and_raise_exception(
                ValueError('{} is unsupported'.format(self.profile['arch'])))

    def __check_build_id(self):
        if 'build' in self.profile:
            build = int(self.profile['build'])
            logger.debug("{} is a valid build id".format(build))
            if build < 0:
                raise(ValueError('build id must be a positive integer'))
        else:
            logger.warning('No build id in the profile')

    def __repr__(self):
        return self.profile


if __name__ == '__main__':
    import sysconfig
    buildprofile = BuildProfile(
        osp.join(sysconfig.get_path('data'), 'config/config.json'))
    pprint(buildprofile)