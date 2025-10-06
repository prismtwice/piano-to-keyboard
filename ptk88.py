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
# MAPPING
# --------------------------
mapping = {}

def add_octave_mapping(octave, white_keys, sharp_keys):
    white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    sharp_notes = ['C#', 'D#', 'F#', 'G#', 'A#']

    for note, key in zip(white_notes, white_keys):
        mapping[note_to_midi[f"{note}_{octave}"]] = [key]

    for note, key in zip(sharp_notes, sharp_keys):
        mapping[note_to_midi[f"{note}_{octave}"]] = ['shift', key]

# Octave 0
mapping[note_to_midi["A_0"]] = ['ctrl', '1']
mapping[note_to_midi["A#_0"]] = ['ctrl', '2']
mapping[note_to_midi["B_0"]] = ['ctrl', '3']

# Octave 1
oct1_keys = ['4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't']
for i, note in enumerate(NOTE_NAMES):
    mapping[note_to_midi[f"{note}_1"]] = ['ctrl', oct1_keys[i]]

# Octaves 2–6
octave_key_layouts = {
    2: (['1', '2', '3', '4', '5', '6', '7'], ['1', '2', '4', '5', '6']),
    3: (['8', '9', '0', 'q', 'w', 'e', 'r'], ['8', '9', 'q', 'w', 'e']),
    4: (['t', 'y', 'u', 'i', 'o', 'p', 'a'], ['t', 'y', 'i', 'o', 'p']),
    5: (['s', 'd', 'f', 'g', 'h', 'j', 'k'], ['s', 'd', 'g', 'h', 'j']),
    6: (['l', 'z', 'x', 'c', 'v', 'b', 'n'], ['l', 'z', 'c', 'v', 'b']),
}

for octave, (white, sharp) in octave_key_layouts.items():
    add_octave_mapping(octave, white, sharp)

# Octave 7
mapping[note_to_midi["C_7"]] = ['m']
ctrl_keys_7 = ['y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j']
sharps_7 = ['C#_7', 'D_7', 'D#_7', 'E_7', 'F_7', 'F#_7', 'G_7', 'G#_7', 'A_7', 'A#_7', 'B_7', 'C_8', 'C#_8']
for note_name, key in zip(sharps_7, ctrl_keys_7):
    mapping[note_to_midi[note_name]] = ['ctrl', key]

# Octave 8
mapping[note_to_midi["D_8"]] = ['ctrl', 'k']

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
