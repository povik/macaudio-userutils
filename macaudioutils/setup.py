import alsaaudio
import fnmatch

from .pcm import *
from .sweep import *

class Card:
	def __init__(self, no=0):
		self.no = no
		self.mixers = [
			alsaaudio.Mixer(name, cardindex=self.no)
			for name in alsaaudio.mixers()
		]

	def find_mixer(self, pattern):
		return [el for el in self.mixers \
				if fnmatch.fnmatch(el.mixer(), pattern)]

	@property
	def name(self):
		return self.mixers[0].cardname()

card = Card()

def _set_elem(el, val):
	if type(val) is bool:
		el.setmute(not val)
	elif type(val) is str:
		_, options = el.getenum()
		el.setenum(options.index(val))
	elif type(val) is int:
		el.setvolume(val)
	else:
		raise ValueError(f"unsupported type in setting of {el.mixer()}: {type(val)}")

def set(pattern, val):
	matches = card.find_mixer(pattern)
	if not len(matches):
		raise ValueError(f"no matches for {repr(pattern)}")

	for el in matches:
		_set_elem(el, val)
