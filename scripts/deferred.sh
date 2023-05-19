#!/bin/sh
mount -t debugfs debugfs /sys/kernel/debug/
cat /sys/kernel/debug/devices_deferred
