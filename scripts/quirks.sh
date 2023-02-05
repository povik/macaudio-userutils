#!/bin/sh
set -e

echo $1 > /sys/module/snd_soc_tas2764/parameters/apple_quirks
