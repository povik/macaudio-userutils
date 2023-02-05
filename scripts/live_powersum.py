#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from select import poll
from macaudioutils.setup import *

set("Headphone Playback Mux", "Primary")
set("Speaker Playback Mux", "Secondary")
set("*ISENSE", True)
set("*VSENSE", True)

indicator = card.find_mixer("Speakers Up Indicator")[0]
ind_poll = poll()
for desc in indicator.polldescriptors():
	ind_poll.register(*desc)

def interpret_sense_data(data):
	I, V = data[:, 0::2].astype(np.float32) * 3.75 / (2 ** 15), \
		   data[:, 1::2].astype(np.float32) * 14 / (2 ** 15)
	return I, V

def coroutine(pcm_info):
	data = yield
	I, V = interpret_sense_data(data)
	avg_watts = np.mean(I * V, axis=0)
	sum_joules = np.zeros_like(avg_watts)

	print("")

	while True:
		data = yield
		I, V = interpret_sense_data(data)

		curr_watts = np.maximum(np.mean(I * V, axis=0),
								np.zeros_like(avg_watts))
		avg_watts = 0.02 * curr_watts + 0.98 * avg_watts

		period_joules = np.maximum(np.sum(I * V, axis=0) / pcm_info['rate'],
							       np.zeros_like(avg_watts))
		sum_joules += period_joules

		print("  ".join(
			f"CH{idx}: {j:2.03f} J ({w:2.04f} W) "
			for idx, w, j in zip(range(len(avg_watts)),
								 avg_watts, sum_joules)
		), end="    \r")

while True:
	# Wait until speakers are up
	while indicator.getmute()[0]:
		ind_poll.poll()
		indicator.handleevents()

	p = SenseProcessor(coroutine, nchans=2)
	p.start()

	# Wait until speakers are down
	while not indicator.getmute()[0]:
		ind_poll.poll()	
		indicator.handleevents()

	p.stop()
