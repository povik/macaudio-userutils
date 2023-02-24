#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from macaudioutils.utils import *
import argparse
import struct
import glob
from pprint import pprint

require_debugfs()

def read_int32ul(f):
    return struct.unpack("I", f.read(4))[0]

def read_int64ul(f):
    return struct.unpack("Q", f.read(8))[0]

# derived from m1n1's OSSerialize
class OSSerialize:
    @classmethod
    def parse(self, stream, verbose=False):
        hdr = read_int32ul(stream)
        if hdr != 0xd3:
            raise Exception("Bad header")

        obj, last = self.parse_obj(stream, verbose=verbose)
        assert last
        return obj

    @classmethod
    def parse_obj(self, stream, level=0, verbose=False):
        # align to 32 bits
        pos = stream.tell()
        if pos & 3:
            stream.read(4 - (pos & 3))

        tag = read_int32ul(stream)

        last = bool(tag & 0x80000000)
        otype = (tag >> 24) & 0x1f
        size = tag & 0xffffff

        if verbose:
            print(f"{'  '*level} @{stream.tell():d} {otype} {last} {size}")

        if otype == 1:
            d = {}
            for i in range(size):
                k, l = self.parse_obj(stream, level + 1, verbose)
                assert not l
                v, l = self.parse_obj(stream, level + 1, verbose)
                assert l == (i == size - 1)
                d[k] = v
        elif otype == 2:
            d = []
            for i in range(size):
                v, l = self.parse_obj(stream, level + 1, verbose)
                assert l == (i == size - 1)
                d.append(v)
        elif otype == 4:
            d = read_int64ul(stream)
        elif otype == 9:
            d = stream.read(size).decode("utf-8")
        elif otype == 10:
            d = stream.read(size)
        elif otype == 11:
            d = bool(size)
        else:
            raise Exception(f"Unknown tag {otype}")

        if verbose and otype not in [1, 2]:
            print(f"{'  '*level}  => {d}")
        return d, last

argparser = argparse.ArgumentParser()
argparser.add_argument("-v", "--verbose", action="store_true")
args = argparser.parse_args()

elements_hits = glob.glob("/sys/kernel/debug/sound/card?/elements")

if not len(elements_hits):
    sys.stderr.write("There doesn't seem to be a DCP sound card. (No matches for '/sys/kernel/debug/sound/card?/elements')")
    sys.exit(1)

data = OSSerialize.parse(open(elements_hits.pop(), "rb"), args.verbose)
if not args.verbose:
    pprint(data)
