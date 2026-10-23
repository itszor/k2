#!/usr/bin/env python3
"""The demo, unpacked by its own decruncher, and the modules it holds.

    unpack.py           game/!k2/k2 -> unpacked/k2 (the image the decruncher
                        leaves at &8000), and unpacked/<module> for each
                        module in it (at its address there)

k2 is an absolute (&FF8) packed with a decruncher on its end, the one
DFI's FishTank2 has too: its first word branches to &FA6A8, which copies
the decruncher above where the unpacked image will end, calls
OS_SynchroniseCodeAreas on that copy (R1 = its start: the end of the
image), decrunches the program backwards into &8000-&3EA9AC, synchronises
it and enters it at &8000 - an AIF image, a C program on the Shared C
Library. Here it runs under SuperSpider's tools/arm2.py until it reaches
&8000.

The image holds three modules, each with its length in the word before it
(as OS_Module 10, insert from memory, takes it), which the program inserts
where they are: TimPlayer (the music player), ShonkFS (a filing system
for the music file) and AutoVCache.
"""
import os
import struct
import sys

SS = os.environ.get('SUPERSPIDER', os.path.expanduser('~/stuff/superspider'))
sys.path.insert(0, os.path.join(SS, 'tools'))
import arm2  # noqa: E402

TOP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
APP = os.path.join(TOP, 'game', '!k2')
OUT = os.path.join(TOP, 'unpacked')
BASE = 0x8000
SYNC = 0x2006E                          # XOS_SynchroniseCodeAreas
MODULES = [('timplayer', 0x15ED6C, b'TimPlayer'), ('shonkfs', 0x242694, b'ShonkFS'),
           ('autovcache', 0x2F248C, b'AutoVCache')]


def find(d, name):
    """a RISC OS file in a host directory: any case, any ,load-exec suffix"""
    for f in os.listdir(d):
        if f.split(',')[0].lower() == name.lower():
            return os.path.join(d, f)
    raise FileNotFoundError(os.path.join(d, name))


def unpack(packed):
    m = arm2.ARM(memsize=0x1000000)
    m.mem[BASE:BASE + len(packed)] = packed
    m.r[13], m.r[14] = 0, 0xDEAD0
    end = []

    def swi(m, n, pc):
        if n != SYNC:
            raise RuntimeError('unpack: SWI &%X at &%X' % (n, pc))
        if not end:                     # the decruncher's copy of itself
            end.append(m.r[1])
    m.swi_handler = swi
    m.r[15] = BASE
    while not (m.r[15] == BASE and m.steps):
        m.step()
        if m.steps > 2_000_000_000:
            raise RuntimeError('unpack: no end, pc=&%X' % m.r[15])
    if not end:
        raise RuntimeError('unpack: entered &8000 without synchronising the decruncher')
    return bytes(m.mem[BASE:end[0]])


def main():
    os.makedirs(OUT, exist_ok=True)
    image = unpack(open(find(APP, 'k2'), 'rb').read())
    open(os.path.join(OUT, 'k2'), 'wb').write(image)
    print('k2: %d bytes at &%X' % (len(image), BASE))
    for name, at, title in MODULES:
        o = at - BASE
        n = struct.unpack_from('<I', image, o - 4)[0]
        t = o + struct.unpack_from('<I', image, o + 16)[0]
        if not image[t:t + len(title)] == title or n > len(image) - o:
            sys.exit('unpack: no %s module at &%X (a damaged dump?)' % (title.decode(), at))
        open(os.path.join(OUT, name), 'wb').write(image[o:o + n])
        print('%s: %d bytes at &%X' % (name, n, at))


if __name__ == '__main__':
    main()
