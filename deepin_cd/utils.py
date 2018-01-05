# /usr/bin/env python3

import os
import logging
import subprocess

logger = logging.getLogger(__name__)

def log_and_raise_exception(e):
    if isinstance(e, Exception):
        logger.exception(e)
        raise(e)

def get_native_arch():
    """
    Execute "dpkg-architecture" on debian based OS to get/guess host arch
    """
    if os.path.isfile('/etc/debian_version'):
        logger.debug('Get host arch via dpkg-architecture')
        try:
            proc = subprocess.run(['dpkg-architecture', '-q', 'DEB_HOST_ARCH'],
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)
            if proc.returncode == 0:
                return proc.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            pass
    return None

def runcmd(cmd, env={}, cwd=None):
    """
    Execute cmd with env, print output to stdout and check return code
    """
    logger.debug('runcmd {} with env {}, working dir {}'.format(cmd, env, cwd))
    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          env=env,
                          cwd=cwd) as proc:
        for line in proc.stdout:
            print(line, end='')
    if proc.returncode != 0:
        raise(ChildProcessError)