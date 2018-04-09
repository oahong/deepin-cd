#! /usr/bin/python3

import os.path as osp
import logging
import git

from os import makedirs
from deepin_cd.utils import log_and_raise_exception

logging.getLogger(__name__)


class DebianCDRepo:
    """ Initialize a debian-cd code repository from repository"""

    repository = "http://git.sh.deepin.cn/hhao/debian-cd"

    def __init__(self, dir, branch="master"):
        self.dir = dir
        self.branch = branch

    def fetch_src(self):
        """
        Download debian-cd source code to self.dir
        """
        makedirs(self.dir, exist_ok=True)
        if osp.isdir(osp.join(self.dir, '.git')):
            # we're already living in debian-cd git repository
            try:
                git.Repo(self.dir).remotes.origin.pull()
            except git.exc. GitCommandError as e:
                log_and_raise_exception(e)
        elif osp.isdir(self.dir):
            git.Repo.clone_from(
                DebianCDRepo.repository,
                self.dir,
                branch=self.branch)
        else:
            e = NotADirectoryError('{} is not a directory'.format(self.dir))
            log_and_raise_exception(e)

if __name__ == '__main__':
    repo = DebianCDRepo(osp.join(b'/tmp', b'debian-cd'))
    repo.fetch_src()