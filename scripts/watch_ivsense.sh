#!/bin/sh
set -e
DIR=`dirname "$0"`
killall speaker-test || true
$DIR/setup_ivsense.py
speaker-test -D hw:0,1 -F S32_LE -c 1 -r 48000 -t sine &
arecord -D hw:0,2 -f S16_LE -c 12 -t raw -r 48000 -t raw | xxd -g 2 -c 24 | awk 'NR == 1 || NR % 1028 == 0'
