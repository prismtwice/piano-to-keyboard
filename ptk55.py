import mido
from pynput.keyboard import Controller, Key
import sys

keyboard = Controller()

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

note_to_midi = {}
for octave in range(0, 10):
    for i, name in enumerate(NOTE_NAMES):
        midi_num = 12 * (octave + 1) + i
        note_to_midi[f"{name}_{octave}"] = midi_num

note_to_midi["A_0"] = 21
note_to_midi["A#_0"] = 22
note_to_midi["B_0"] = 23

# --------------------------
# MAPPING (Updated)
# --------------------------
mapping = {}

# White note order
white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
sharp_notes = {'C', 'D', 'F', 'G', 'A'}  # Notes that have sharps

# Keyboard keys to map from '1' to 'm'
key_sequence = [
    '1', '2', '3', '4', '5', '6', '7',
    '8', '9', '0', 'q', 'w', 'e', 'r',
    't', 'y', 'u', 'i', 'o', 'p', 'a',
    's', 'd', 'f', 'g', 'h', 'j', 'k',
    'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm'
]

current_midi_note = 36  # Start at C2 (MIDI 36)

for key in key_sequence:
    note_index = (current_midi_note - 12) % 12  # To get note name from MIDI
    note_name = NOTE_NAMES[note_index]

    # Add natural note
    mapping[current_midi_note] = [key]

    # Add sharp if applicable
    if note_name in sharp_notes:
        mapping[current_midi_note + 1] = ['shift', key]
        current_midi_note += 2  # Skip over the sharp we just assigned
    else:
        current_midi_note += 1

# --------------------------
# KEYBOARD HELPERS
# --------------------------

held_main_keys = set()             # e.g. {'1', 'q'}
note_to_main_key = {}             # MIDI note -> '1'
main_key_to_note = {}             # '1' -> MIDI note

def press_key_combo(combo, note):
    if isinstance(combo, list):
        modifiers = combo[:-1]
        key = combo[-1]

        # If main key is held by another note, release it first
        if key in held_main_keys:
            previous_note = main_key_to_note.get(key)
            if previous_note != note:
                keyboard.release(key)
                held_main_keys.remove(key)

        # Press modifiers
        for mod in modifiers:
            keyboard.press(getattr(Key, mod) if hasattr(Key, mod) else mod)

        # Press main key
        keyboard.press(key)
        held_main_keys.add(key)
        main_key_to_note[key] = note

        # Release modifiers
        for mod in reversed(modifiers):
            keyboard.release(getattr(Key, mod) if hasattr(Key, mod) else mod)

    else:
        key = combo
        if key in held_main_keys:
            previous_note = main_key_to_note.get(key)
            if previous_note != note:
                keyboard.release(key)
                held_main_keys.remove(key)

        keyboard.press(key)
        held_main_keys.add(key)
        main_key_to_note[key] = note

    note_to_main_key[note] = key  # Track which key this note uses

def release_key_combo(combo, note):
    if isinstance(combo, list):
        key = combo[-1]
    else:
        key = combo

    # Only release if the note still owns the key
    current_owner = main_key_to_note.get(key)
    if current_owner == note:
        keyboard.release(key)
        held_main_keys.discard(key)
        main_key_to_note.pop(key, None)

    note_to_main_key.pop(note, None)

# --------------------------
# MIDI LISTENER
# --------------------------

def main():
    print("Piano-to-key v1.0")
    inputs = mido.get_input_names()
    if not inputs:
        print("No MIDI devices found.")
        sys.exit(1)

    print("Available MIDI Devices:")
    for i, name in enumerate(inputs):
        print(f"{i}: {name}")

    port = mido.open_input(inputs[0])
    print(f"\nListening on: {inputs[0]}\n")

    active_notes = {}  # MIDI note -> key combo
    sustain = False

    try:
        for msg in port:
            if msg.type == 'note_on' and msg.velocity > 0:
                note = msg.note
                if note in mapping:
                    key_combo = mapping[note]
                    press_key_combo(key_combo, note)
                    active_notes[note] = key_combo

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                note = msg.note
                if note in active_notes:
                    key_combo = active_notes[note]
                    release_key_combo(key_combo, note)
                    del active_notes[note]

            elif msg.type == 'control_change' and msg.control == 64:
                if msg.value >= 64 and not sustain:
                    keyboard.press(Key.space)
                    sustain = True
                elif msg.value < 64 and sustain:
                    keyboard.release(Key.space)
                    sustain = False

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        port.close()

# --------------------------
# RUN
# --------------------------
if __name__ == "__main__":
    main()
