#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import argparse
from macaudioutils.setup import *

argparser = argparse.ArgumentParser()
argparser.add_argument("-A", "--amplitude", type=float, default=0.9,
					   help="sweep amplitude")
argparser.add_argument("-r", "--rate", type=int, default=48000,
					   help="sample rate")
argparser.add_argument("-d", "--duration", type=float, default=1.0,
					   help="sweep duration (in seconds)")
argparser.add_argument("-f", "--Ftop", type=float, default=None,
					   help="sweep top frequency")
argparser.add_argument("-P", "--pad", type=float, default=0.3,
					   help="silent padding ahead of sweep (in seconds)")
argparser.add_argument("-p", "--psd", type=str, default=None,
					   help="filename for a power spectral density plot of sense data")
args = argparser.parse_args()

set("Headphone Playback Mux", "Primary")
set("Speaker Playback Mux", "Secondary")
set("Speaker", 40)
set("ISENSE", True)
set("VSENSE", True)

signal = sweep(args.duration, Fs=args.rate, Ftop=args.Ftop, eps=0.03)

pad = int(args.pad * args.rate)
rec = SenseRecorder(rate=args.rate)

with rec:
	pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, channels=1,
						rate=args.rate,
						format=alsaaudio.PCM_FORMAT_S32_LE,
						periodsize=160,
						mode=alsaaudio.PCM_NORMAL, device="hw:0,1")
	pcm.write(b"\x00\x00\x00\x00" * pad)
	pcm.write((signal * args.amplitude * 2**31).astype(np.int32).tobytes())

if args.psd:
	from matplotlib import pyplot as plt
	plt.figure(figsize=(8, 8))
	plt.psd(rec.data[pad:,0], label="I", Fs=args.rate)
	plt.psd(rec.data[pad:,1], label="V", Fs=args.rate)
	plt.legend()
	plt.savefig(args.psd)
