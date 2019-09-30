# TODO: un-hardcode output directories and filenames from functions:
# simplify_midi_file, create_ascending_chromatic, create_descending_chromatic.

import re, time, mido
from mido import MidiFile, MidiTrack

# Prints a summary count of messages in MIDI file
def summarize_midi_file(filename):
#{
    message_type_count = {}
    non_zero_time_count = {}
    midi_file_in = MidiFile(filename)
    
    print(f'\nMIDI File: {filename}:')
    print("  PPQN:", midi_file_in.ticks_per_beat)
    for i, track in enumerate(midi_file_in.tracks):
        print(f"  Track {i+1}: {track}")
        for message in track:
            message_type_count[message.type] = message_type_count.get(message.type, 0) + 1
            if message.time != 0: non_zero_time_count[message.type] = non_zero_time_count.get(message.type, 0) + 1
    
    print("  Contained messages:")
    for k in message_type_count.keys():
        if k not in non_zero_time_count: print(f"    {k}: {message_type_count[k]}")
        else: print(f"    {k}: {message_type_count[k]} (nonzero times: {non_zero_time_count[k]})")
#}

# This creates simplified, single-track MIDI files that contain only 'note_on',
# 'control_change' (with control == 64, i.e. sustain peddle), and 'end_of_track'. 
def simplify_midi_file(filename, track_number):
#{
    midi_file_in = MidiFile(filename)
    track = midi_file_in.tracks[track_number]
    
    midi_file_out = MidiFile(ticks_per_beat=midi_file_in.ticks_per_beat)
    track_out = MidiTrack()
    
    for message in track:
        if message.type == 'note_on' or message.type == 'end_of_track' or \
          (message.type == 'control_change' and message.control == 64):
            track_out.append(message)

    #midi_file_out.tracks.append(track)        # Adds original in track 0 for comparison
    midi_file_out.tracks.append(track_out)     
        
    # Save the file appropriately
    outname = re.sub(r'.mid$', '_simple.mid', filename)
    outname = re.sub(r'midi_originals', 'midi_cleaned', outname)
    
    print("Saving to file:", outname)
    midi_file_out.save(outname)
#}

# This fcn plays a MIDI file if output port is appropriately
# registered and a DAW is open to receive messages, translate
# them to an actual audio signal and relay them to speakers
def play_midi_file(filename, portname, display_messages=True):
#{
    with mido.open_output(portname) as output:
        try:
        #{
            midi_file_in = MidiFile(filename)
            print(f'Attempting to play: \'{filename}...\'')
            
            t0 = time.time()
            for message in midi_file_in.play():
            #{
                output.send(message)
                if display_messages: 
                    print(f"<message {message}>")
            #}
            print('play time: {:.2f} s (expected {:.2f})'.
                  format(time.time() - t0, midi_file_in.length))
        #}
        except KeyboardInterrupt:
            print()
            output.reset()
#}


# TODO: these should be collapsed into a single fucntion
# These fcns create simplified MIDI files of a chromatic 
# scall (ascending and descending) of all 88 piano keys
def create_ascending_chromatic():
#{
    midi_file = MidiFile()
    track_out = MidiTrack()
     
    for note in range(21, 109):
        track_out.append(mido.Message('note_on', note=note, velocity=127, time=750))
        track_out.append(mido.Message('note_on', note=note, velocity=0, time=200))
    
    track_out.append(mido.MetaMessage('end_of_track'))
    midi_file.tracks.append(track_out)
    midi_file.save('../data/midi_cleaned/88_Key_Ascending_Chromatic_Scale.mid')
#}

def create_descending_chromatic():
#{
    midi_file = MidiFile()
    track_out = MidiTrack()
     
    for note in range(108, 20, -1):
        track_out.append(mido.Message('note_on', note=note, velocity=127, time=750))
        track_out.append(mido.Message('note_on', note=note, velocity=0, time=200))
    
    track_out.append(mido.MetaMessage('end_of_track'))
    midi_file.tracks.append(track_out)
    midi_file.save('../data/midi_cleaned/88_Key_Descending_Chromatic_Scale.mid')
#}
