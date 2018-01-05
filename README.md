# deepin-cd

deepin-cd customization script
It's A helper script to wrapper around debian-cd (with some deepin specific dirty hacks)

usage:
    deepin-cd -c config.json -b BUILD_ID
  or
    deepin-cd -r /work/repository -o /work/iso -w /work/mkiso/debian-cd -b BUILD_ID -a ARCH

- BUILD_ID is ISO image build number, should be an integer
- ARCH is the architecture, either mips64el or sw64, script itself will guess arch