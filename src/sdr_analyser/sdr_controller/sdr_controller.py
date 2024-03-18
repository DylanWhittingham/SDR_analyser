from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
import sigmf
import os
from sigmf import SigMFFile
import datetime as dt
from sigmf.utils import get_data_type_str


sdr = RtlSdr()

activeFile = 'sdr_iq_data/iq_samples.sigmf-data'

sampleRate = 102e4
freq = 174e6
gain = 50
sampleTime = 5
signalDuration = sampleTime / sdr.sample_rate
currentTime = dt.datetime.utcnow().isoformat()+'Z' #ZULU time

#SDR Configuration
sdr.sample_rate = sampleRate  # Msps
sdr.center_freq = freq # Hz
sdr.gain = gain #dB

iqSamples = sdr.read_samples(1*sampleRate)

for x in range(sampleTime):
    np.append(iqSamples, sdr.read_samples(1*sampleRate))

iqSamples = iqSamples.astype(np.complex64)

iqSamples.tofile(activeFile)

meta = SigMFFile(
    data_file=activeFile, # extension is optional
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

loadedIQ = np.fromfile(activeFile, np.complex64)

print('Sampling @', sdr.sample_rate, 'Msps')
print('Frequency @', sdr.center_freq, 'Hz')
print('Sampling Length @', signalDuration, 'Seconds')

plt.psd(loadedIQ, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6, detrend='mean')
plt.spe
print(iqSamples)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.show()

