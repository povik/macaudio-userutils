#!/bin/sh
set -e

echo 1 > /sys/module/snd_soc_macaudio/parameters/please_blow_up_my_speakers
echo "sound" > /sys/bus/platform/drivers/snd-soc-macaudio/bind
