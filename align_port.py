import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u, constants as c
import pplib


norm = True
subbands = 8
delta_DM = 0
portrait = "dm_test/J1012_dm_test.port"

#Find the DM that maximizes the standard deviation
def find_DM(datafile, delta_DM=np.linspace(-1e-2,1e-2), return_std=False):
    """Find the change in DM that maximizes the standard deviation across the profile
    Parameter
    ---------
    datafile : str
         name of portrait file
    delta_DM : np.ndarray, optional
         array of delta DM values
    return_std : bool, optional
         whether to return the array of standard deviations or not
    Returns
    -------
    float
        Change in DM that maximizes standard deviation
    std : np.ndarray
        standard deviation as a function of delta_DM (if requested)
    """
    dp = pplib.DataPortrait(datafile=datafile)
    phase = np.arange(dp.port.shape[1])/dp.port.shape[1]
    P = dp.Ps[0]*u.s
    timebin = (phase*P)[1] - (phase*P)[0]
    std = np.zeros(len(delta_DM))
    for j in range(len(delta_DM)):
        # for the full portrait
        time_delay_portrait = (dp.freqs**-2-dp.freqs.max()**-2)*4.15e6*u.ms*delta_DM[j]
        shift_bins_portrait = np.int16(np.round((time_delay_portrait[0] / timebin).decompose()))
        shifted_portrait = np.zeros_like(dp.port)
        for i in range(dp.port.shape[0]):
            shifted_portrait[i] = np.roll(dp.port[i], shift_bins_portrait[i])
        # sum over all channels
        profile = shifted_portrait.sum(axis=0)
        # and compute standard deviation over phase bins
        std[j] = profile.std()
    # find the index where std is max
    j=np.where(std==std.max())[0][0]
    # fit a parabola to interpolate
    fit = np.polyfit(delta_DM[j-2:j+2], std[j-2:j+2],2)
    if not return_std:
        return -fit[1]/2/fit[0]
    return -fit[1]/2/fit[0], std

dp = pplib.DataPortrait(datafile=portrait)

nchan_per_subband = dp.port.shape[0] // subbands
profiles = np.zeros((subbands, dp.port.shape[1]))
freqs = np.zeros((subbands))*u.MHz
phase = np.arange(dp.port.shape[1])/dp.port.shape[1]
P = dp.Ps[0]*u.s
timebin = (phase*P)[1] - (phase*P)[0]


#Calculating the average profile for each frequency subband
for i in range(subbands):
    d = dp.port[i*nchan_per_subband:(i+1)*nchan_per_subband]
    w = dp.weights[0,i*nchan_per_subband:(i+1)*nchan_per_subband]
    profiles[i] = (d.T*w).sum(axis=1).T/w.sum()
    # weighted average frequency too
    freqs[i] = (dp.freqs[0,i*nchan_per_subband:(i+1)*nchan_per_subband]*w).sum()/w.sum()*u.MHz
    if norm:
        profiles[i] /= profiles[i].max()
        

plt.clf()

#Calculating the time delay between each fequency bin and the maximum frequency bin. Pulsar handbook equation 4.7
time_delay = (freqs.to(u.MHz).value**-2 - freqs.max().to(u.MHz).value**-2)*4.15e6*u.ms*delta_DM

#How many phase bins to shift subbands based on time-delay
shift_bins = np.int16(np.round((time_delay / timebin).decompose()))


for i in range(subbands):
    plt.plot(phase, np.roll(profiles[i],shift_bins[i]), label=f"{freqs[i].value} MHz")


plt.xlabel('Phase')
plt.ylabel('Amplitude')
plt.legend()
plt.savefig('shifted_profiles.pdf')

# do the same operations for the full portrait
time_delay_portrait = (dp.freqs**-2-dp.freqs.max()**-2)*4.15e6*u.ms*delta_DM
shift_bins_portrait = np.int16(np.round((time_delay_portrait[0] / timebin).decompose()))
shifted_portrait = np.zeros_like(dp.port)
for i in range(dp.port.shape[0]):
    shifted_portrait[i] = np.roll(dp.port[i], shift_bins_portrait[i])
    
plt.clf()
plt.imshow(shifted_portrait,aspect='auto')
plt.savefig('shifted_portrait.pdf')

delta_DM, std = find_DM(portrait, np.linspace(-1e-2,1e-2), return_std=True)
plt.clf()
plt.plot(np.linspace(-1e-2,1e-2), std, delta_DM, std.max(),'ro')
plt.xlabel('$\Delta$DM')
plt.ylabel('Standard Deviation')
plt.savefig('find_dm_correction.pdf')
