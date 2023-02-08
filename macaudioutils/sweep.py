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
	Ftop = Ftop or (Fs / 2)
	t = np.arange(Fs * duration) / Fs
	return np.real(np.exp(2j*np.pi * Ftop \
							/ duration * t**2/2)) \
		* planck_taper(len(t), eps)

def sine(duration=1.0, Fs=48000, F=1000, phase=0):
	t = np.arange(Fs * duration) / Fs
	return np.real(np.exp(1j*(2*np.pi * F * t + phase)))

def main():
    import argparse
    import wave

    argparser = argparse.ArgumentParser()
    argparser.add_argument("WAVE_FILENAME", type=str)
    argparser.add_argument("-r", "--rate", type=int, default=48000,
                       help="sample rate")
    argparser.add_argument("-d", "--duration", type=float, default=1.0,
                           help="sweep duration (in seconds)")
    argparser.add_argument("-f", "--Ftop", type=float, default=None,
                           help="sweep top frequency")
    args = argparser.parse_args()

    signal = sweep(args.duration, Fs=args.rate, Ftop=args.Ftop, eps=0.03)

    with open(args.WAVE_FILENAME, "wb") as f:
        wave = wave.Wave_write(f)
        wave.setnchannels(1)
        wave.setframerate(args.rate)
        wave.setsampwidth(4)
        wave.writeframes((signal * 0.9 * 2**31).astype(np.int32).tobytes())
        wave.close()

if __name__ == "__main__":
    main()
