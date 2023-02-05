#!/bin/sh

while [ 1 ]; do
	dd if=/dev/zero of=/dev/stdout count=1 bs=1024 | \
		aplay -t raw -r 48000 -f S32_LE "$@"
done
