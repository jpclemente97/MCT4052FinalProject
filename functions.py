def extractMidiData(filename):
    from mido import MidiFile
    from classes import File
    from classes import Note

    # Extract information from filename format
    filenameInfo = filename.split("_")
    style = filenameInfo[1]
    tempo = filenameInfo[2]
    # Files are classified as either beats or fills
    isBeat = (filenameInfo[3] == 'beat')
    # The split function keeps the file extension, so we have to get rid of it for the time signature
    timeSignature = filenameInfo[4].replace('.mid', '')
    
    # Extract information from Mido
    mid = MidiFile(filename)   
    ticksPerBeat = mid.ticks_per_beat
    # We will be checking to see how far off every note is from 16th note quantization
    ticksPerSixteenthNote = ticksPerBeat / 4
    
    # There should only be one track per file
    for track in mid.tracks:
        # Keeps track of what time we're at in the MIDI file using the "time" attribute
        # in "note_on" and "note_off" messages
        currentTick = 0
        
        # Dictionary for all of our MIDI instruments (snare, hi-hat, etc.)
        instruments = {}
        
        for msg in track:
            if msg.type == "note_on":
                if(msg.velocity == 0):
                    currentTick += msg.time
                    # Add end tick value to the last note in the list
                    lastNoteIndex = len(instruments[msg.note]) - 1
                    instruments[msg.note][lastNoteIndex].addEndTick(currentTick)
                else:
                    if msg.note not in instruments:
                        # Create new list of notes for new instrument
                        instruments[msg.note] = []

                    currentTick += msg.time
                    # End tick will be added when a note_off message appears
                    instruments[msg.note].append(Note(msg.velocity, currentTick, 0))
            elif msg.type == "note_off":
                currentTick += msg.time
                # Add end tick value to the last note in the list
                lastNoteIndex = len(instruments[msg.note]) - 1
                instruments[msg.note][lastNoteIndex].addEndTick(currentTick)

    return File(filename, ticksPerSixteenthNote, style, tempo, isBeat, timeSignature, instruments)
