#!/usr/bin/env python
import time
import glob

counters_fn = glob.glob("/sys/kernel/debug/apple_leap/*.dsp/core1/counters")[0]
f = open(counters_fn, "rb")

def snap_values():
	idle, busy = 0, 0
	routines = [0] * 8

	f.seek(0)
	for line in f:
		a, b = line.strip().split(b": ", 2)

		if a == b"Idle":
			idle = int(b, 16)
		elif a == b"Busy":
			busy = int(b, 16)
		elif a.startswith(b"Routine #"):
			routine_no = int(a.split(b"#", 2)[1])
			routines[routine_no] = int(b, 16)
	return idle, busy, routines


def delta(a, b):
	return (b - a) % 2**32

spin = "\\-/|"
pivot = snap_values()
try:
	while True:
		time.sleep(0.1)
		vals = snap_values()
		idle, busy = delta(pivot[0], vals[0]), delta(pivot[1], vals[1])
		routines = [delta(a, b) for a, b in zip(pivot[2], vals[2])]
		base = idle + busy
		text = f" {spin[0]}"; spin = spin[1:] + spin[:1]
		text += f" Usage: {busy / base * 100:03.2f}%"
		for i, rout in enumerate(routines):
			text += f" Rout#{i}: {rout / base * 100:03.2f}%"
		print(text, end="\r")
		pivot = vals
except KeyboardInterrupt:
	print()
