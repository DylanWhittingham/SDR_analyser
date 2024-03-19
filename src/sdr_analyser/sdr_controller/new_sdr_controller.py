from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
import sigmf
from sigmf import SigMFFile, sigmffile
from sigmf.utils import get_data_type_str
import datetime as dt
from pylab import *
from scipy import signal
activeFile = 'sdr_iq_data/iq_samples.sigmf-data'
sdr = RtlSdr()

##configure SDR
sampleRate = 2.048e6 
freq = 174e6
gain = 50
sampleTime = 1
signalDuration = sampleTime / sdr.sample_rate
currentTime = dt.datetime.utcnow().isoformat()+'Z' #ZULU time
sdr.sample_rate = sampleRate  # Msps
sdr.center_freq = freq # Hz
sdr.gain = gain #dB

iqSamples = sdr.read_samples(sampleTime*sampleRate) #make iq

iqSamples = iqSamples.astype(np.complex64)

iqSamples.tofile(activeFile)

meta = SigMFFile(
    data_file=activeFile, 
    global_info = {
        SigMFFile.DATATYPE_KEY: get_data_type_str(iqSamples),  # in this case, 'cf32_le'
        SigMFFile.SAMPLE_RATE_KEY: sdr.sample_rate,
        SigMFFile.AUTHOR_KEY: 'DylanWhittingham@outlook.com',
        SigMFFile.DESCRIPTION_KEY: 'RF Recording of an FM radio',
    }
)

meta.add_capture(0, metadata={
    SigMFFile.FREQUENCY_KEY: sdr.center_freq,
    SigMFFile.DATETIME_KEY: currentTime,
})
meta.validate()
meta.tofile('sdr_iq_data/iq_samples.sigmf-meta') # extension is optional


signal = sigmffile.fromfile(activeFile)
samples = signal.read_samples().view(np.complex64).flatten()

# Get some metadata and all annotations
sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
sample_count = signal.sample_count
signal_duration = sample_count / sample_rate

rel_power, freq = psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6, scale_by_freq=False)

rel_power_db = 10*np.log10(rel_power)
###################
#end of controller#
###################

print(sample_rate)
print(sample_count)
print(signal_duration)

print(rel_power_db)

noise = np.mean(rel_power_db)
signalPow = np.max(rel_power_db)

print(noise)

print(signalPow)

snr = 10 * np.log10(np.max(rel_power) / (np.sum(rel_power) - np.max(rel_power)))
print(snr)
# print('freq', freq)
# print('power', power_db)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.show()