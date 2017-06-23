#! /usr/bin/env python3

import glob
import logging

from subprocess import PIPE, STDOUT
from subprocess import Popen

logger = logging.getLogger(__name__)

def update_boot_menu(bootFolder, id, preseed):
    """
    update boot menu for both pmon and kunlun firmware
    """

    pmon_cfg="""
    default 0
    timeout 3
    showmenu 1

    title Install deepin Server V15 B{3} Via USB(3A2000)
        kernel /dev/fs/fat@usb0/boot/{0}
        initrd /dev/fs/fat@usb0/boot/{1}
        args console=tty file=/cdrom/{2} auto=true

    title Install deepin Server V15 B{3} Via CDROM(3A2000)
        kernel /dev/fs/iso9660@cd0/boot/{0}
        initrd /dev/fs/iso9660@cd0/boot/{1}
        args console=tty file=/cdrom/{2} auto=true
    """

    # TODO: change the menu color
    kunlun_cfg="""
    set default=0
    set timeout=3
    set menu_color_normal=white/black
    set menu_color_highlight=yellow/black

    menuentry 'Install deepin Server V15 B{4} (3A2000)' {
	set root=(${root})
	linux (${root})/boot/{0} console=tty file=/cdrom/{2}
	initrd (${root})/boot/{1}
	boot
    }
    """

    # get kernel, initrd is always initrd.gz
    vmlinux = glob.glob(os.path.join(bootDir, "vmlinux*"))
    vmlinux = [os.path.basename(v) for v in vmlinux]

    bootcfg = [os.path.join(bootFolder, cfg) for cfg in
               ['boot.cfg', 'grub.cfg']]
    contents = [pmon_cfg, kunlun_cfg]

    for idx, cfg in enumerate(bootcfg):
        with open(cfg, 'w') as menu:
            logger.debug("Update boot menu {} with entry: {}".format(cfg, vmlinux[0]))
            menu.write(contents[idx].format(vmlinux[0], 'initrd.gz', id, preseed))

def set_value(x, y, allow_empty = True):
    result = x or y
    if result or allow_empty:
        logger.debug("Set value to %s" % result)
        return result
    else:
        raise ValueError("value is empty when allow_empty is {}".format(allow_empty))

def runcmd(cmd, env={}, cwd=None):
    """
    Run cmd with env, check return code and print output to stdout
    """
    logger.debug('runcmd {} with env {}, working dir {}'.format(cmd, env, cwd))
    #TODO: use cwd parameter
    with Popen(cmd, stdout=PIPE, stderr=STDOUT,
               universal_newlines=True, env=env, cwd=cwd) as proc:
        for line in proc.stdout:
            print(line, end='')
