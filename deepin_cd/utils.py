#! /usr/bin/env python3

import glob

PMONCFG="""
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
KUNLUNCFG="""
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

def updateBootMenu(bootFolder, id, preseed):
    """
    update boot menu for both pmon and kunlun firmware        
    """

    # get kernel, initrd is always initrd.gz
    vmlinux = glob.glob(os.path.join(bootDir, "vmlinux*"))
    vmlinux = [os.path.basename(v) for v in vmlinux]


    bootcfg = [os.path.join(bootFolder, cfg) for cfg in
               ['boot.cfg', 'grub.cfg']]
    fileContents = [PMONCFG, KUNLUNCFG]

    for idx, cfg in enumerate(bootcfg):
        with open(cfg, 'w') as cfg:
            cfg.write(fileContents[idx].format(vmlinux[0], 'initrd.gz', id, preseed))
