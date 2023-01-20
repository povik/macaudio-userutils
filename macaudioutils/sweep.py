import numpy as np
import math

def planck_taper(N, eps):
	ret = np.zeros(N, dtype=np.float64)
	N -= 1
	ret[0] = 0
	Neps_floor = math.floor(N * eps)
	for i in range(1, Neps_floor + 1):
		ret[i] = 1.0/(1 + np.exp(eps*N/i - eps*N/(eps*N - i)))
	ret[Neps_floor + 1:N - Neps_floor + 1] = 1.0
	ret[N - Neps_floor - 1:] = ret[Neps_floor + 1::-1]
	return ret

def sweep(duration=1.0, Fs=48000, Ftop=None, eps=0.1):
	Ftop = Ftop or Fs
	t = np.arange(Fs * duration) / Fs
	return np.real(np.exp(2j*np.pi * Ftop \
							/ duration * t**2/4)) \
		* planck_taper(len(t), eps)
