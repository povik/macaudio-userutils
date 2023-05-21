#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pyqtgraph as pg
from macaudioutils.setup import *

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle("Mic PSD")

pcm = PCM(True, "hw:0,7", periodsize=4096)

curves = []
for i in range(pcm.nchannels):
	plot = win.addPlot(colspan=1)
	plot.setLabel('bottom', 'Frequency', 'kHz')
	plot.setLabel('left', 'Log Power', 'dB')
	plot.setYRange(-110, 10)
	label = pg.LabelItem(f"Chan {i}", size='20pt')
	label.setParentItem(plot)
	label.setPos(60, 0)
	curves.append(plot.plot())
	win.nextRow()

class DataThread(pg.QtCore.QThread):
	newPoints = pg.QtCore.Signal(object)

	def run(self):
		fft_len = pcm.period_size // 2
		window = np.hamming(fft_len * 2)
		navg_periods = int(pcm.rate / fft_len / 30) + 1
		window_weight = np.sum(window**2)

		while True:
			acc = np.zeros((fft_len, pcm.nchannels))
			for _ in range(navg_periods):
				data = pcm.read_period()
				period_fd = np.fft.rfft(data * window.reshape(-1, 1), axis=0)[:fft_len,:]
				acc += np.real(np.conjugate(period_fd) * period_fd)
			psd_log = np.log10(acc / navg_periods / window_weight) * 10
			self.newPoints.emit((np.linspace(0, pcm.rate / 2, fft_len), psd_log))

def setPoints(points):
	x, all_ys = points
	for curve, y in zip(curves, all_ys.swapaxes(0, 1)):
		curve.setData(x=x, y=y)

dt = DataThread()
dt.newPoints.connect(setPoints)
dt.start()

if __name__ == '__main__':
    pg.exec()
