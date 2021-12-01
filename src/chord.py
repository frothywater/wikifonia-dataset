from mido import MetaMessage, MidiFile, MidiTrack


def accumulate_time(messages: list):
    if len(messages) == 0:
        return
    current = 0
    result = []
    for msg, delta_time in messages:
        current += delta_time
        result.append((msg, current))
    return result


def deaccumulate_time(messages: list):
    if len(messages) == 0:
        return
    result = []
    for i in range(len(messages)):
        if i == 0:
            result.append(messages[0])
        else:
            msg, abs_time = messages[i]
            _, prev_time = messages[i - 1]
            result.append((msg, abs_time - prev_time))
    return result


def add_chord_markers(file: str, chords: list):
    mid = MidiFile(file)
    track: MidiTrack = mid.tracks[1]
    messages = [(msg, msg.time) for msg in track]

    messages = accumulate_time(messages)
    for name, offset in chords:
        marker_message = MetaMessage("marker")
        marker_message.text = name.replace("-", "b")
        abs_time = int(offset * mid.ticks_per_beat)
        messages.append((marker_message, abs_time))
    messages.sort(key=lambda x: x[1])
    messages = deaccumulate_time(messages)

    track.clear()
    for msg, delta_time in messages:
        msg.time = delta_time
        track.append(msg)
    mid.save(file)
