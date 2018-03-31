#! /usr/bin/env python3

import json
import logging
import sysconfig

from pathlib import Path
from deepin_cd.utils import log_and_raise_exception
from deepin_cd.config import __codenames__

logging.getLogger(__name__)


class Task(object):
    """
    Return a list of packages defined in taskfiles
    """
    taskfile = 'deepin.json'

    def __init__(self, codename):
        self.codename = codename
        self.task_dir = codename
        self.packages = self.read_package_list()

    @property
    def codename(self):
        return self.__codename

    @codename.setter
    def codename(self, codename):
        if codename in __codenames__:
            logging.debug('set codename to {}'.format(codename))
            self.__codename = codename
        else:
            # fallback to 'stable' if we get invalid codename
            logging.debug('codename unknown, fallback to stable suite')
            self.__codename = 'stable'

    @property
    def task_dir(self):
        return self.__task_dir

    @task_dir.setter
    def task_dir(self, __task_dir):
        path = Path(sysconfig.get_path('data')) / 'tasks' / self.codename
        if Path.is_dir(path):
            logging.debug('set task_dir to {}'.format(path))
            self.__task_dir = path
        else:
            log_and_raise_exception(NotADirectoryError(path))

    def read_package_list(self):
        """
        Read package list from software groups defined in taskfile
        Each software group itself is another json format file, in which we'll 
        define a group of packages to be included in the installation media
        exclude.json will define packages that should never be placed in the 
        installtion media
        """
        packages = []

        taskfiles = list(self.task_dir.glob("*.json"))
        logging.debug('taskfiles: {}'.format(taskfiles))
        if self.task_dir / self.taskfile not in taskfiles: 
            log_and_raise_exception(
                FileNotFoundError('No {} task file'.format(self.taskfile)))

        logging.info('Read software groups from {}'.format(self.taskfile))
        groups = [c + '.json' for c in
            self.read_task_file(self.taskfile)['groups']]
        logging.debug("software groups in taskfile: {}".format(groups))
        logging.info('Read package list from group files {}'.format(groups))

        pl = list(map(self.read_task_file, groups))
        for e in pl:
            for p in list(e.values()):
                packages.extend(p)

        # remove duplicates elements
        packages = set(packages)

        # remove packages recorded in exclude.json
        excludes = set(self.read_task_file('exclude.json')['excludes'])
        packages.difference_update(excludes)
        return list(packages)

    def read_task_file(self, task):
        taskp = self.task_dir / task
        logging.debug('Reading package list from {}'.format(taskp))
        with open(taskp, 'r') as t:
            return json.load(t)


if __name__ == '__main__':
    task = Task('kui')
    print(task.packages)