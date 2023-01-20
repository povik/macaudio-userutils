import alsaaudio
import time
from threading import Thread

class Recorder(Thread):
	def __init__(self, **kwargs):
		super().__init__()
		self.should_exit = False
		self.pcm = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
					 mode=alsaaudio.PCM_NONBLOCK,
					 periodsize=320, **kwargs)
		self.pcm_info = self.pcm.info()
		self._data = []

	@property
	def sample_dtype(self):
		return {
			"S16_LE": np.dtype('<i2'),
			"S32_LE": np.dtype('<i4'),
			"FLOAT_LE": np.dtype('<f4'),
		}[self.pcm_info['format_name']]

	@property
	def data(self):
		data_bytes = b"".join(self._data)
		return np.frombuffer(data_bytes, dtype=self.sample_dtype) \
			.reshape((-1, self.pcm_info['channels']))

	def run(self):
		while not self.should_exit:
			size, buf = self.pcm.read()
			if size == 0:
				time.sleep(0.001)
				continue
			if size < 0:
				print(f"Capture error: {size}",
				      file=sys.stderr)
			self._data.append(buf)
		self.pcm.close()

	def __enter__(self):
		self.start()
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.should_exit = True
		self.join()

class SenseRecorder(Recorder):
	def __init__(self, nchans=2, rate=48000):
		Recorder.__init__(self, channels=nchans,
				  format=alsaaudio.PCM_FORMAT_S16_LE,
				  device="hw:0,2", rate=rate)
