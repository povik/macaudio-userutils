import pathlib
import glob

class SpeakerChannel:
	def __init__(self, amp_dt_path):
		self.amp_dt_path = amp_dt_path
		self.name = self.lookup_amp_prop("sound-name-prefix", b"Speaker").decode("ascii")
		self.sense_slots = (
			int.from_bytes(self.lookup_amp_prop("ti,imon-slot-no", b"\x00"), byteorder="big"),
			int.from_bytes(self.lookup_amp_prop("ti,vmon-slot-no", b"\x02"), byteorder="big"),
		)

	def lookup_amp_prop(self, prop, default=None):
		proppath = self.amp_dt_path.joinpath(prop)
		if not proppath.exists():
			return default
		else:
			return proppath.read_bytes()

	def __repr__(self):
		return f"<channel {self.name}>"

	def dump(self):
		print(f"{self.name}:")
		print(f"\tAmp DT Path: {self.amp_dt_path}")
		print(f"\tI/V sense slots: {self.sense_slots}")

def compatible_matches(path, bait):
	with path.joinpath("compatible").open("rb") as f:
		compatibles = f.read().split(b"\0")
	return not set(compatibles).isdisjoint(set(bait))

SPEAKER_AMP_COMPATIBLES = [
	b"ti,tas5770",
	b"ti,sn012776",
]

speaker_list = [
	SpeakerChannel(i2c_dev_path)
	for i2c_dev_path
	in pathlib.Path("/proc/device-tree/soc/").glob("i2c@*/codec@??")
	if compatible_matches(i2c_dev_path, SPEAKER_AMP_COMPATIBLES)
]

speaker_list.sort(key=lambda ch: ch.sense_slots)

if __name__ == "__main__":
	for chan in speaker_list:
		chan.dump()
