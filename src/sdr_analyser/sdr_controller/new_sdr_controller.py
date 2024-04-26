from rtlsdr import RtlSdr #imports rtlsdr wrapper
import numpy as np #imports numpy
import matplotlib.pyplot as plt #imports pyplot
from matplotlib import mlab #imports mlab
import sigmf #imports sigmf
from sigmf import SigMFFile, sigmffile #imports sigmffile
from sigmf.utils import get_data_type_str #imports sigmf utils
import datetime as dt #imports datetime
from pylab import * #imports pylab
from scipy import signal #imports scipy


print('Welcome to SDR Analyser!\n') #prints a welcome message
filename = input('Please input the name of your IQ File') #prompts user input

activeSignal = 'sdr_iq_data/'+filename+'.sigmf-data' #string var for setting file name
activeMetadata = 'sdr_iq_data/'+filename+'.sigmf-meta' #string var for setting meta file name
sdr = RtlSdr() #defines rtlsdr

def get_db(sample): #function for converting values to decibels
    return ((10*np.log10(sample))) #returns result as a float

def get_noiseAverage(sample): #function for getting the average noise present in a signal
    return int(np.mean(get_db(sample))) #returns result as an int

def get_signalPower(sample): #function for getting max signal power
    return int(np.max(get_db(sample))) #returns result as an int

def get_snr(sample): #function for calculating snr
    return int(get_db(np.max(sample) / (np.sum(sample) - np.max(sample)))) #returns result as an int

# configure SDR
sampleRate = 2.048e6 #sets sample rate using a float
freq = 174e6 #sets freq using a float
gain = 50 #sets gain using a literal
sampleTime = 5 #sets sample time using a literal
signalDuration = sampleTime / sdr.sample_rate #gets signal recording duration by dividing sample time by sample rate
currentTime = dt.datetime.utcnow().isoformat()+'Z'  # ZULU time defined as a string
sdr.sample_rate = sampleRate  # Msps #configures sdr to set sample rate 
sdr.center_freq = freq  # Hz #configures sdr to set freq
sdr.gain = gain  # dB #configures sdr to set gain

iqSamples = (sdr.read_samples(sampleTime*sampleRate).astype(np.complex64)) #creates complex64 array 
iqSamples.tofile(activeSignal) #save iq samples to i/o

#defines metadata keys for recording
meta = SigMFFile( 
    data_file=activeSignal,
    global_info={
        SigMFFile.DATATYPE_KEY: get_data_type_str(iqSamples),
        SigMFFile.SAMPLE_RATE_KEY: sdr.sample_rate,
        SigMFFile.AUTHOR_KEY: 'DylanWhittingham@outlook.com',
        SigMFFile.DESCRIPTION_KEY: 'RF Recording of an FM radio',
    }
)

#adds capture point to metadata, this is essential a note on the recording
meta.add_capture(0, metadata={
    SigMFFile.FREQUENCY_KEY: sdr.center_freq,
    SigMFFile.DATETIME_KEY: currentTime,
})
meta.validate() #validates given data so far is fine to save
meta.tofile(activeMetadata)

signal = sigmffile.fromfile(activeSignal) #reads recording stored so far to sigmf format
samples = signal.read_samples().view(np.complex64).flatten() #reads stored array into samples

# Get some metadata and all annotations
sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY) #gets sample rate from stored metadata
sample_count = signal.sample_count #gets sample count from stored metadata
signal_duration = sample_count / sample_rate #calculate signal duration

#creates a psd with NFFT applied
power, freq = psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, 
                  Fc=sdr.center_freq/1e6, scale_by_freq=False)

print('Noise Average is ', get_noiseAverage(power), 'dB') #prints average noise in dB
print('Signal Power is', get_signalPower(power), 'dB') #prints signal power in dB
print('SNR is ', get_snr(power), 'dB') #prints SNR
#calcuates quality of SNR
if get_snr(power)>0: 
    print('Good Signal, above noisefloor')
else:
    print('Bad Signal, below noisefloor')
#outputs the PSD to a pyplot
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.show()
