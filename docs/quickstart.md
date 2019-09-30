## Project: music-writer 

**Note: this project is a work in progress, still very early stage and not cleaned up for easily understandable presentation.**

The goal of this project is automated transcription of solo piano recordings, or more precisely to create simplified MIDI files given WAV audio (as there are existing tools to translate MIDI into musical notation). This project was inspired by the improvisations of jazz pianist Brad Mehldau, and though automated musical transcription has received a lot of attention, the programs I could find produced essentially gibberish given Meldau recordings. Please see the project blog for a more detailed description.
___

### Installation:

The repository is setup for pipenv configuration management, thus you'll find a Pipfile rather than requirements.txt file.  
You may access installation instructions for pipenv here: [Pipenv Installation Instructions](https://pypi.org/project/pipenv/)

Once pipenv has been successfully installed, the following commands may be executes to install the rubiks-cube project:

```
$ git clone https://github.com/ajdonich/music-writer.git
$ cd music-writer
$ pipenv install
$ pipenv --dev install
```
___

### Execution:

Again, the project is in early stages and has not be manicured for presentation, however, please feel free to run through the notebooks. These should all execute but (my apologies) they are not well commented or organized at this point, many still with draft versions of functions etc. Generally, you can find .py files in the *mwriter* directory and .ipynb files in the *notebooks* directory. The *sandbox* directory is just very rough, scratch pad stuff at this point.

To run IPython/Jupyter notebooks, assure you are in the *music-writer* root directory, then launch a notebook session from the command line using:

```
$ pipenv shell
$ jupyter lab
```

Then from within the notebook session that is launched in your browser, navigate to the notebooks directory. This directory contains the following set of .ipynb files that you're free to run in whatever order you prefer:

1. data_generation.ipynb
2. learn_fft.ipynb
3. neural_fft.ipynb
4. process_audio_data.ipynb

They explore training a variety of NN architectures, pre-processing several audio files (with conversions to spectral formats) and MIDI file handing (though to really look at MIDI files, you'll need to open with a DAW such as Garage Band or otherwise).
