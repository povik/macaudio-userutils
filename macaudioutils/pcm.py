import alsaaudio
import time
import numpy as np
import sys
from threading import Thread

class CaptureThread(Thread):
	def __init__(self, **kwargs):
		super().__init__()
		self.should_exit = False
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
					 mode=alsaaudio.PCM_NONBLOCK,
					 periodsize=320, **kwargs)
		self.pcm_info = self.pcm.info()

	def run(self):
		while not self.should_exit:
			size, buf = self.pcm.read()
			if size == 0:
				time.sleep(0.001)
				continue
			if size < 0:
				print(f"Capture error: {size}",
				      file=sys.stderr)
			samples = np.frombuffer(buf, dtype=self.sample_dtype) \
						.reshape((-1, self.pcm_info['channels']))
			self.process_period(samples)

		self.pcm.close()

	@property
	def sample_dtype(self):
		return {
			"S16_LE": np.dtype('<i2'),
			"S32_LE": np.dtype('<i4'),
			"FLOAT_LE": np.dtype('<f4'),
		}[self.pcm_info['format_name']]

	def stop(self):
		self.should_exit = True
		self.join()

class Recorder(CaptureThread):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._chunks = []

	def process_period(self, samples):
		self._chunks.append(samples)

	@property
	def data(self):
		return np.concatenate(self._chunks)

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.stop()

class SenseRecorder(Recorder):
	def __init__(self, nchans=2, rate=48000):
		Recorder.__init__(self, channels=nchans,
				  format=alsaaudio.PCM_FORMAT_S16_LE,
				  device="hw:0,2", rate=rate)

class SenseProcessor(CaptureThread):
	def __init__(self, consumer, nchans=2, rate=48000):
		CaptureThread.__init__(self, channels=nchans,
				 			   format=alsaaudio.PCM_FORMAT_S16_LE,
							   device="hw:0,2", rate=rate)
		self.consumer = consumer(self.pcm_info)
		next(self.consumer)

	def process_period(self, samples):
		self.consumer.send(samples)
