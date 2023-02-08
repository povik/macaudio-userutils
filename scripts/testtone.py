#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import argparse
from macaudioutils.setup import *

db = -16

set("Headphone Playback Mux", "Primary")
set("Speaker Playback Mux", "Secondary")
set("*Speaker", 100 + db)
set("*ISENSE", True)
set("*VSENSE", True)

ftest = 43.0664
rate = 48000
duration = 200
pad = 1
plot = "plot.png"
#amplitude = 1

signal = sine(duration, Fs=rate, F=ftest)
#amplitude = (sine(duration, Fs=rate, F=2, phase = -np.pi/2) + 1) * 0.5 * 0.9 + 0.05
amplitude = 1

print(amplitude)
#print(len(signal), len(amplitude), max(amplitude), min(amplitude))

#amplitude=1

pad = int(pad * rate)
rec = SenseRecorder(rate=rate, nchans=12)

channel = 2
channels = 6

with rec:
	pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, channels=channels,
						rate=rate,
						format=alsaaudio.PCM_FORMAT_S32_LE,
						periodsize=512,
						mode=alsaaudio.PCM_NORMAL, device="hw:0,1")
	pcm.write(b"\x00\x00\x00\x00" * pad * channels)
	data = np.zeros((len(signal), channels))
	data[:, channel] = signal * amplitude * (2**31 - 1)
	pcm.write(data.astype(np.int32).tobytes())

np.save(f"ivsense_c{channel}_{db}dB_sine.npy", rec.data[pad:,:])

if plot:
	from matplotlib import pyplot as plt
	plt.figure(figsize=(8, 8))
	plt.psd(rec.data[pad:,0], label="I", Fs=rate)
	plt.psd(rec.data[pad:,1], label="V", Fs=rate)
	plt.legend()
	plt.savefig(plot)
