# Traktor 4 Mappings for Akai LPD8 MK2

# LPD8 MK2 Reflect

A Python script to control and animate the LEDs on the Akai LPD8 MK2 via MIDI SysEx messages.

## Features

* **Interactive MIDI port selection**: Console menu to choose input/output ports at runtime.
* **Initialization animation**: Hue‑cycling across all pads for a set duration, aborts on first pad activity, ends with all‑white frame.
* **Background breathing effect** for pad groups:

  * Pads 1–2 (BREATH\_GROUP1): red → yellow breath.
  * Pads 5–6 (BREATH\_GROUP2): green → blue breath.
  * Pads 3–4 (STATIC\_BLUE\_PADS): static light blue.
  * Pads 7–8 (STATIC\_ORANGE\_PADS): static orange.
* **Pad press state toggling**: Tracks on/off state for each pad (notes 36–43).
* **Ripple animation** on press for configured pads: white ripple expands outward over nearby pads.
* **Console feedback**: Colored text output for note events, pad indices, and status.
* **Graceful shutdown**: Clears all LEDs and closes ports when exiting (Ctrl+C).

## Requirements

* Python 3.6 or newer (tested on Python 3.10)
* [mido](https://pypi.org/project/mido/)
* [python-rtmidi](https://pypi.org/project/python-rtmidi/) (MIDI backend for mido)
* [colorama](https://pypi.org/project/colorama/)

## Installation

```bash
pip install mido python-rtmidi colorama
```

## Configuration

At the top of `lpd8_reflect.py`, adjust these constants to suit your setup:

```python
# MIDI ports (None to prompt at runtime)
IN_PORT_IDX    = None
OUT_PORT_IDX   = None

# Pad groups (0‑indexed: pad 1 is index 0)
BREATH_GROUP1     = {0, 1}
BREATH_GROUP2     = {4, 5}
STATIC_BLUE_PADS   = {2, 3}
STATIC_ORANGE_PADS = {6, 7}
RIPPLE_PADS        = BREATH_GROUP1.union(BREATH_GROUP2)

# Animation timings (in seconds)
BREATH_PERIOD     = 2.0
BG_INTERVAL       = 0.05
RIPPLE_DURATION   = 0.1
MAX_RIPPLE_RADIUS = 2
RIPPLE_INTERVAL   = RIPPLE_DURATION / (MAX_RIPPLE_RADIUS + 1)

# Initialization animation settings
INIT_DURATION = 5.0
INIT_INTERVAL = 0.05
```

## Quick Start: loopMIDI + Traktor

1. **Install loopMIDI**: Download and install from [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html). Launch loopMIDI and create a virtual ports named, for example, `LPD8MK2Reflect'.

2. **Configure ports**:

   * In loopMIDI, click the **+** button to add ports.
   * Rename them precisely to match the names you’ll select in the script and Traktor.

3. **Run the Python script**:

   ```bash
   python lpd8_reflect.py
   ```

   * When prompted, choose **MIDI Input**: `LPD8MK2Reflect`.
   * Then choose **MIDI Output**: `LPD8 MK2`. This should be to your LPD8 hardware.
 
4. **Load the Traktor mapping**:

   * Open **Traktor** and go to **Preferences** > **Controller Manager**.
   * Click **Add** > **Generic MIDI**.
   * For **Device**, select the imported `.tsi` file.
   * Set **In-Port** to `LPD8 MK2`, **Out-Port** to `LPD8MK2Reflect`.
   * Make sure the mapping is **Enabled**.

5. **Use**: With your LPD8 MK2 connected and Traktor running, pressing pads will now trigger the LED animations in the script while controlling your configured FX in Traktor.

# Traktor Mapping File
The Traktor . tsi file included in this repository provides a preset mapping for two‑channel mixing with two FX groups (FX Unit 1 and FX Unit 2). The last effect in each group is mapped to the final two MIDI knobs—assigned to Turntable FX and Darkmatter.

# Inputs

| Pad 5                     | Pad 6                     | Pad 7                        | Pad 8                        | Knob 1         | Knob 2         | Knob 3         | Knob 4                   |
|---------------------------|---------------------------|------------------------------|------------------------------|----------------|----------------|----------------|--------------------------|
| FX Unit 1 On (Note E2)    | FX Unit 2 On (Note C♯2)   | FX Unit 1 Toggle (Note F♯2)   | FX Unit 1 Toggle (Note G2)   | FX Unit 1 CC 070 | FX Unit 1 CC 071 | FX Unit 1 CC 072 | Button 3 Hold (CC 073)   |

| Pad 1                     | Pad 2                     | Pad 3                        | Pad 4                         | Knob 5         | Knob 6         | Knob 7         | Knob 8                   |
|---------------------------|---------------------------|------------------------------|-------------------------------|----------------|----------------|----------------|--------------------------|
| FX Unit 1 On (Note C2)    | FX Unit 2 On (Note F2)    | FX Unit 2 Toggle (Note D2)   | FX Unit 2 Toggle (Note D♯2)   | FX Unit 2 CC 074 | FX Unit 2 CC 075 | FX Unit 2 CC 076 | Button 3 Hold (CC 077)   |

Outputs

| Pad 5                          | Pad 6                          | Pad 7                          | Pad 8                          |
|--------------------------------|--------------------------------|--------------------------------|--------------------------------|
| FX Unit 1 On LED (Note E2)     | FX Unit 2 On LED (Note F2)     | Button 1 LED (Note F♯2)        | Button 2 LED (Note G2)        |

| Pad 1                          | Pad 2                          | Pad 3                          | Pad 4                          |
|--------------------------------|--------------------------------|--------------------------------|--------------------------------|
| FX Unit 2 On LED (Note C2)     | FX Unit 2 On LED (Note C♯2)    | Button 1 LED (Note D2)         | Button 2 LED (Note D♯2)        |

---

| Comment     | Control        | I/O   | Assignment | Mode    | Mapped to       |
|-------------|----------------|-------|------------|---------|-----------------|
| [Knob 1]    | Knob 1         | In    | FX Unit 1  | Direct  | Ch01.CC.070     |
| [Knob 2]    | Knob 2         | In    | FX Unit 1  | Direct  | Ch01.CC.071     |
| [Knob 3]    | Knob 3         | In    | FX Unit 1  | Direct  | Ch01.CC.072     |
| [Knob 4]    | Button 3       | In    | FX Unit 2  | Hold    | Ch01.CC.073     |
| [Knob 5]    | Knob 1         | In    | FX Unit 2  | Direct  | Ch01.CC.074     |
| [Knob 6]    | Knob 2         | In    | FX Unit 2  | Direct  | Ch01.CC.075     |
| [Knob 7]    | Knob 3         | In    | FX Unit 2  | Direct  | Ch01.CC.076     |
| [Knob 8]    | Button 3       | In    | FX Unit 2  | Hold    | Ch01.CC.077     |
| [Pad 1]     | FX Unit 1 On   | In    | Deck B     | Toggle  | Ch10.Note.C2    |
| [Pad 1 LED] | FX Unit 1 On   | Out   | Deck B     | Output  | Ch10.Note.C2    |
| [Pad 2]     | FX Unit 2 On   | In    | Deck B     | Toggle  | Ch10.Note.C#2   |
| [Pad 2 LED] | FX Unit 2 On   | Out   | Deck B     | Output  | Ch10.Note.C#2   |
| [Pad 3]     | Button 1       | In    | FX Unit 2  | Toggle  | Ch10.Note.D2    |
| [Pad 3 LED] | Button 1       | Out   | FX Unit 2  | Output  | Ch10.Note.D2    |
| [Pad 4]     | Button 2       | In    | FX Unit 2  | Toggle  | Ch10.Note.D#2   |
| [Pad 4 LED] | Button 2       | Out   | FX Unit 2  | Output  | Ch10.Note.D#2   |
| [Pad 5]     | FX Unit 1 On   | In    | Deck A     | Toggle  | Ch10.Note.E2    |
| [Pad 5 LED] | FX Unit 1 On   | Out   | Deck A     | Output  | Ch10.Note.E2    |
| [Pad 6]     | FX Unit 2 On   | In    | Deck A     | Toggle  | Ch10.Note.F2    |
| [Pad 6 LED] | FX Unit 2 On   | Out   | Deck A     | Output  | Ch10.Note.F2    |
| [Pad 7]     | Button 1       | In    | FX Unit 1  | Toggle  | Ch10.Note.F#2   |
| [Pad 7 LED] | Button 1       | Out   | FX Unit 1  | Output  | Ch10.Note.F#2   |
| [Pad 8]     | Button 2       | In    | FX Unit 1  | Toggle  | Ch10.Note.G2    |
| [Pad 8 LED] | Button 2       | Out   | FX Unit 1  | Output  | Ch10.Note.G2    |

## Additional Information
Midi SysEx inplementation info can be found here : https://github.com/john-kuan/lpd8mk2sysex

## License

This project is released under the MIT License.

