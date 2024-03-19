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
import os.path


print('Welcome to SDR Analyser!\n')
filename = input('Please input the name of your IQ File')

activeSignal = 'sdr_iq_data/'+filename+'.sigmf-data'
activeMetadata = 'sdr_iq_data/'+filename+'.sigmf-meta'
sdr = RtlSdr()

def get_db(sample):
    return ((10*np.log10(sample)))

def get_noiseAverage(sample):
    return int(np.mean(get_db(sample)))

def get_signalPower(sample):
    return int(np.max(get_db(sample)))

def get_snr(sample):
    return int(get_db(np.max(sample) / (np.sum(sample) - np.max(sample))))

# configure SDR
sampleRate = 2.048e6
freq = 174e6
gain = 50
sampleTime = 5
signalDuration = sampleTime / sdr.sample_rate
currentTime = dt.datetime.utcnow().isoformat()+'Z'  # ZULU time
sdr.sample_rate = sampleRate  # Msps
sdr.center_freq = freq  # Hz
sdr.gain = gain  # dB

iqSamples = (sdr.read_samples(sampleTime*sampleRate).astype(np.complex64))
iqSamples.tofile(activeSignal)

meta = SigMFFile(
    data_file=activeSignal,
    global_info={
        SigMFFile.DATATYPE_KEY: get_data_type_str(iqSamples),
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
meta.tofile(activeMetadata)

signal = sigmffile.fromfile(activeSignal)
samples = signal.read_samples().view(np.complex64).flatten()

# Get some metadata and all annotations
sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
sample_count = signal.sample_count
signal_duration = sample_count / sample_rate


power, freq = psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6,
                  Fc=sdr.center_freq/1e6, scale_by_freq=False)

print('Noise Average is ', get_noiseAverage(power), 'dB')
print('Signal Power is', get_signalPower(power), 'dB')
print('SNR is ', get_snr(power), 'dB')

if get_snr(power)>0:
    print('Good Signal, above noisefloor')
else:
    print('Bad Signal, below noisefloor')

plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.show()