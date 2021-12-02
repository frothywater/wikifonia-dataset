from mido import MetaMessage, MidiFile, MidiTrack


def add_chord_markers(file: str, chords: list):
    """Add chord markers in given MIDI file and chord list.
    
    Chords are a list of tuple in form of (name, quarter offset).
    """
    mid = MidiFile(file)
    track: MidiTrack = mid.tracks[1]

    markers: list = []
    for name, offset in chords:
        marker = MetaMessage("marker")
        marker.text = name.replace("-", "b")
        marker.time = 0
        markers.append((marker, int(offset * mid.ticks_per_beat)))

    msg_index, marker_index = 0, 0
    current_tick = 0
    while msg_index < len(track) and marker_index < len(markers):
        current_tick += track[msg_index].time
        if markers[marker_index][1] <= current_tick:
            if track[msg_index].type == "note_on":
                track.insert(msg_index, markers[marker_index][0])
            else:
                track.insert(msg_index + 1, markers[marker_index][0])
            msg_index += 1
            marker_index += 1
        msg_index += 1

    mid.save(file)
