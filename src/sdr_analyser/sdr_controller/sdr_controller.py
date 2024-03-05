from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab

sdr = RtlSdr()

sample_rate = 102e4
freq = 174e6
gain = 50


#SDR Configuration
sdr.sample_rate = sample_rate  # Msps
sdr.center_freq = freq # Hz
sdr.gain = gain

iq_samples = sdr.read_samples(1*sample_rate)



for x in range(5):
    np.append(iq_samples, sdr.read_samples(1*sample_rate))

iq_samples = iq_samples.astype(np.complex64)

iq_samples.tofile('sdr_iq_data/iq_samples.iq')

loaded_iq = np.fromfile('sdr_iq_data/iq_samples.iq', np.complex64)

print('Sampling @', sdr.sample_rate, 'Msps')
print('Frequency @', sdr.center_freq, 'Hz')

plt.psd(loaded_iq, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6, detrend='mean')
print(iq_samples)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.show()

