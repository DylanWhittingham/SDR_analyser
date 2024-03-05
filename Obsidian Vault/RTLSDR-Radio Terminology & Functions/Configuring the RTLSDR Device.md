***************************
*****
## **Sample Rate**

Sample rate sets the rate at which the ADC samples the received signal.  If we set this too low, the waveform of the received signal will become aliased (distorted), making it unreadable.  

>To determine what frequency we can accurately sample, we use the Nyquist Frequency formula.
>
>$f_{\mathrm{N}}=\frac{1}{2 \mathrm{~d} t}$
>
>$\mathrm{~d} t$ is our sample rate.
>$f_{\mathrm{N}}$ is the Nyquist frequency.



>We implement this in the code via:
>
>`sdr.sample_rate`

For instance, if we wanted to sample a signal at 175e6 MHz, we would need a sample rate of 350e6 MHz