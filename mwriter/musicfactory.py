import re
import numpy as np
from scipy.io import wavfile

import mido
from mido import MidiFile

from mwriter.abstractfactory import MLDataFactory, MLDataSet


DEFAULT_BPM = 120

class MusicFactory(MLDataFactory):
#{
    # Implement MLDataFactory's abstract creator method 
    def create_dataset(self, ds_name, input_files):
    #{
        switcher = {
            'train_nfreq_1':    self.create_nfreq_1,
            'validate_nfreq_1': self.create_nfreq_1
        }

        assert ds_name in switcher, f"Unknown dataset name: {ds_name}"
        return switcher[ds_name](input_files)
    #}

    def create_nfreq_1(self, input_files):
    #{
        wav_filename, midi_filename = input_files

        # Read wav file (for now discard the 2nd stereo track) 
        rate, data = wavfile.read(wav_filename); data = data[:,0]

        freq_window = (27.5, 4186.0)    # Window of interest: principal piano freqs: A0 to C8 (27.5 to 4186.0 Hz)
        NFFT = int(rate / 1.635)        # Init NFFT for minimum piano semitone: A0 to A#0 (29.135 - 27.5 = 1.635 Hz)
        stride = int(NFFT/2)            # Overlap FFT windows by 50 percent of NFFT 

        # Perform FFTs and then reshape FFT data for DenseNet
        spectral, fft_imin, fft_imax, sec_per_step = self.perform_fft(wav_filename, data, rate, NFFT, stride, freq_window)
        X = self.format_spectral_data(spectral, time_batch=1, freq_window=(fft_imin, fft_imax))
        print(f"Input data shape: {X.shape}")

        # Generate label dataset
        Y = self.generate_contiguous_labels(MidiFile(midi_filename), len(spectral), sec_per_step)
        print(f"Output data shape: {Y.shape}\n")

        return MLDataSet(X,Y) 
    #}

    def freq_to_fftbin(self, freq, freq_resolution): return freq/freq_resolution
    def fftbin_to_freq(self, fft_bin, freq_resolution): return fft_bin*freq_resolution

    def perform_fft(self, data, rate, NFFT, stride, freq_window=None, filename='undefined'):
    #{
        """
        Args:
            data: 1-D array, time-domain audio samples
            rate: int, sampling rate of the data array
            NFFT: int, size (in samples) of the window over which to perform each FFT
            stride: int stride/overlap size (in samples) between each FFT (expecting stride <= NFFT) 
            freq_window: length 2 tuple floats, lower and upper bound of a freq window of interest
                if freq_window is None, values default to full spectrum of the FFT'ed audio data
                (note: full frequency spectrum returned in specral list regardless of these values)
            filename: used only for logging purposes
        
        Return:
            spectral: list of 1-D power spectrum arrays, one for each FFT window of audio data 
            fft_imin: int, index/bin number in specral arrays corresponding to LOWER bound of freq_window
            fft_imax: int, index/bin number in specral arrays corresponding to UPPER bound of freq_window
            
        """

        # Just clip the last segement that is < NFFT
        clipped_length = data.shape[0] - (data.shape[0] % NFFT)

        # Perform the actual FFTs (using Hann window fcn)
        hann_window_fcn = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, NFFT, False)))
        
        # Power spectra calculated as modulus/abs (which is real) of the complex values returned from the rFFT
        spectral = [np.abs(np.fft.rfft(data[i:i+NFFT] * hann_window_fcn)) for i in range(0, clipped_length, NFFT-stride)]
        
        freq_resolution = rate / NFFT
        freq_array = np.fft.rfftfreq(NFFT, d=1.0/rate)

        # Default window of interest to full spectrums
        fft_imin = 0; fft_imax = spectral[0].shape[0]
        freq_intrest_min = 0; freq_intrest_max = self.fftbin_to_freq(fft_imax, freq_resolution)
        
        if freq_window != None:
        #{
            freq_intrest_min = freq_window[0]
            freq_intrest_max = freq_window[1] 
            
            fft_imin = int(np.floor(self.freq_to_fftbin(freq_intrest_min, freq_resolution)))
            fft_imax = int(np.ceil(self.freq_to_fftbin(freq_intrest_max, freq_resolution)))
        #}
        
        # Just collecting meta-data to print
        min_array, max_array = [], []
        min_window_array, max_window_array = [], []
        for spectrum in spectral:
        #{
            min_array.append(np.min(spectrum))
            max_array.append(np.max(spectrum))
            min_window_array.append(np.min(spectrum[fft_imin:fft_imax]))
            max_window_array.append(np.max(spectrum[fft_imin:fft_imax]))
        #}

        response_min = np.min(min_array)
        response_max = np.max(max_array)
        rsp_window_min = np.min(min_window_array)
        rsp_window_max = np.max(max_window_array)
        clipped_samps = data.shape[0] - clipped_length
        sec_per_step = (data.shape[0])/(rate*len(spectral))

        print(f"Wav file: {filename} \
            \nWav file sampling rate: {rate} \
            \nWav file length: {data.shape[0]/rate} sec \
            \nClipping last: {clipped_samps} samps ({clipped_samps*1000/rate}ms) \
            \nNFFT: {NFFT} samples (~{int(round(NFFT*1000/rate))}ms) \
            \nFFT stride/overlap size: {stride}  samples (~{int(round(stride*1000/rate))}ms) \
            \nNumber of time steps: {len(spectral)} \
            \nDuration per time step: {sec_per_step*1000}ms \
            \nSpectra freq window of interest: \
            \n  min: {freq_intrest_min} Hz (fft bin: {fft_imin}) \
            \n  max: {freq_intrest_max} Hz (fft bin: {fft_imax}) \
            \n  => x-axis plotting size = {fft_imax - fft_imin} \
            \nSpectra freq resolution: {freq_resolution} Hz \
            \nSpectra number frequencies: {NFFT//2+1} \
            \n  (check spectral[0].shape: {spectral[0].shape}) \
            \n  (check freq_array.shape: {freq_array.shape}) \
            \nSpectral response extremes: \
            \n  min (interest window): {rsp_window_min} \
            \n  min (full spectrum):   {response_min} \
            \n  max (interest window): {rsp_window_max} \
            \n  max (full spectrum):   {response_max} \
            \n  => y-axis plotting size: {rsp_window_max - rsp_window_min} \n")
        
        return spectral, fft_imin, fft_imax, sec_per_step
    #}

    # This scales the data to between [0,1]
    def format_spectral_data(self, spectral_list, time_batch, freq_window):
    #{
        m = len(spectral_list)
        fft_imin = freq_window[0]
        fft_imax = freq_window[1]
        n_freq = fft_imax - fft_imin
        X = np.zeros((m, n_freq, time_batch))
        
        # Calc standard dev for feature scaling
        spectral_array = np.asarray(spectral_list)
        standev = np.std(spectral_array[:, fft_imin:fft_imax])
        
        # Zero pad a time_batch at the end
        zpad = np.zeros((time_batch, spectral_list[0].shape[0]))
        spectral_array = np.concatenate((spectral_array, zpad))

        for i in range(m):
            fft_block = spectral_array[i:i+time_batch, fft_imin:fft_imax]
            X[i,:,:] = (fft_block / standev).transpose()
            
        print(f"Standard dev of power spectra: {standev} \
            \nFeature scaled spectral response extremes: \
            \n  min: {np.min(X)} \
            \n  max: {np.max(X)} \n")
        
        return X
    #}

    def get_note_strike_times(self, midi_file):
    #{
        tempo = mido.bpm2tempo(DEFAULT_BPM)
        
        assert len(midi_file.tracks) == 1, f"MIDI must have 1 track, not: {len(midi_file.tracks)}"
    
        strike_times = []
        accrued_ticks = 0
        for message in midi_file.tracks[0]: 
        #{
            # Non-zero velocity --> note has been struck
            # Zero velocity --> note has been released
        
            accrued_ticks += message.time
            if message.type == 'note_on' and message.velocity > 0:
                strike_times.append(mido.tick2second(accrued_ticks, midi_file.ticks_per_beat, tempo))
        #}
        
        print(f"Found {len(strike_times)} note strikes in MIDI file: {midi_file.filename}")
        
        return strike_times
    #}

    def generate_contiguous_labels(self, midi_filename, m, sec_per_step):
    #{  
        Y = np.zeros((m,))
        strike_times = self.get_note_strike_times(midi_filename)
        for strike_sec in strike_times: Y[int(strike_sec/sec_per_step)] = 1

        return Y
    #}

    def generate_windowed_labels(self, midi_filename, m, time_batch, sec_per_step, stride=1):
    #{
        # Pad an extra time_batch worth of zeros at the end of contiguous
        Y_contiguous = self.generate_contiguous_labels(midi_filename, m+time_batch, sec_per_step)
        
        strided_steps = np.arange(0, m, stride)
        Y_windowed = np.zeros((len(strided_steps), time_batch))
        
        for i in range(len(strided_steps)): 
            Y_windowed[i,:] = Y_contiguous[strided_steps[i]:strided_steps[i]+time_batch]

        return Y_windowed
    #}

#}