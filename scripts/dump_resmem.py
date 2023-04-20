#!/usr/bin/env python3
import mmap

def read_devmem(base, size):
	with open("/dev/mem", "r+b") as f:
		with mmap.mmap(f.fileno(), size, offset=base) as mm:
			return mm.read(size)


def read_regprop(nodename):
	fn = f"/proc/device-tree/reserved-memory/{nodename}/reg"

	with open(fn, "rb") as f:
		data = f.read()
		cells = [int.from_bytes(data[i:i + 8], byteorder="big") \
			 for i in range(0, len(data), 8)]
		return cells[0], cells[1]

import sys
sys.stdout.buffer.write(read_devmem(*read_regprop(sys.argv[1])))
