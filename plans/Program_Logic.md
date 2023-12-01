# Program Logic

## Definitions

**Trigger Loop** - Trigger loop refers to the internal midinome clock that handles the sending of MIDI events to the Helix. The Midinome will continually send start and stop signals to the Helix to ensure the loop stays in sync with the metronome.

**Helix Loop** - This is the recorded loop on the Helix device. Since Midinome cannot access this audio data, it simply tells the Helix via MIDI in/out when to trigger record, play and stop events.

**Phrase** - The phrase in the Midinome context refers to the duration of the Helix Loop stored in the Trigger Loop. So if you record a total of 16 beats of audio into the Helix Loop, the Phrase would be equal to 16 beats.

**Cut Time** - Cut time is Half-Time, Standard-Time and Double-Time. This does not affect the Trigger Loop, only the Metronome Loop.

## Input Event Summary By Mode

### Live Mode

**Metronome Button**

- **Single Press**: Record Beat / Toggle Audio
- **Double Press**: Change Time Signature _(Only when beat not running)_
- **Triple Press**: Enter BPM Manually _(Only when beat not running)_
- **Hold**: Stop Midinome _(Stop the Metronome Loop, Metronome Audio and Trigger Loop, does not stop the Helix Loop)_

**Trigger Button**

- **Single Press**:
  - Trigger Record Start/Record Stop on next beat _(If Trigger Loop has not been created or has been destroyed.)_
  - Trigger Play/Stop on next beat _(If Trigger Loop is currently running.)_
- **Double Press**: Play/Stop on next downbeat
- **Triple Press**: Play/Stop on next phrase
- **Hold**: Stop/Clear Loop

**+ Button**: Increment Cut Time
**- Button**: Decrement Cut Time

### Config Mode

**Metronome Button**: Select/Confirm
**Trigger Button**: Cancel/Back
**+ Button**: Up/Increment
**- Button**: Down/Decrement

### Time Signature Mode

**Metronome Button**: Confirm
**Trigger Button**: Next
**+ Button**: Increment
**- Button**: Decrement

### Manual BPM Mode

**Metronome Button**: Confirm And Start
**Trigger Button**: Cancel
**+ Button**

- **Single Press**: Increase By 1
- **Hold**: Increase By 20
  **- Button**
- **Single Press**: Decrease By 1
- **Hold**: Decrease By 20

## Input Event Program Logic

- Buttons

  - METRONOME_BUTTON

    - SINGLE_PRESS

      - LIVE_MODE
        - **( Record Beat / Toggle Beat Audio )**
          - _Record if no metronome running, otherwise toggle audio_
      - CONFIG_MODE
        - **( Select Item / Confirm Changes )**
          - _Select an item if there is no active selection, otherwise, confirm changes_
      - TIME_SIGNATURE_MODE

        - **( Confirm Time Signature )**

      - MANUAL_BPM_MODE
        - **( Confirm BPM And Start Playing )**

    - DOUBLE_PRESS

      - IF No Metronome Running
        - **( Enter Time Signature Mode )**

    - TRIPLE_PRESS

      - IF No Metronome Running
        - **( Enter Manual BPM Mode )**

    - HOLD
      - LIVE_MODE
        - **( Stop Metronome And Triggers )**
          - \_Stop the metronome, reset the BPM and break any loops relying on the metronome. This includes MIDI Triggers. This essentially releases control back to the Helix and resets the Midinome to it's default playback state.

  - TRIGGER BUTTON
  - _NOTE Loop Running and Loop Playing are different things. Loop playing means there is a loop of start/stop at the beginning of phrases in Midinome's Event Loop, this loop can be stopped but not deleted to allow the user to start the same recorded lopp again after stopping it previously. Loop Running refers to the Looper Parent Class. If loop running is false, that means the Looper is no longer triggering MIDI events or firing any callbacks from the programs event loop._
    - SINGLE_PRESS
      - LIVE_MODE
        - IF No Loop Running On MidiNome
          - **( Trigger Record Start / Record Stop on Next Beat )**
        - IF Loop Running On MidiNome
          - IF Playing Loop
            - **( Trigger Stop on Next Beat )**
          - IF NOT Playing Loop
            - **( Trigger Play on Next Beat )**
      - CONFIG_MODE
        - **( Cancel / Go Back )**
          - _Cancel changes if there is a current selection, if not go back to config, or if in config go back to live mode_
      - TIME_SIGNATURE_MODE
        - **( Next Number )**
    - DOUBLE_PRESS
      - LIVE_MODE
        - IF Loop Not Running On Midinome
        <!-- Functionality Can Go Here -->
        - IF Loop Running On MidiNome
          - IF Playing Loop
            - **( Trigger Stop On Next Down Beat )**
          - IF NOT Playing Loop
            - **( Trigger Start On Next Down Beat )**
    - TRIPLE_PRESS
      - LIVE_MODE
        - IF Loop Running On MidiNome
          - IF Playing Loop
            - **( Trigger Stop On Next Phrase )**
          - IF NOT Playing Loop
            - **( Trigger Start On Next Phrase )**
    - HOLD
      - LIVE_MODE
        - IF Loop Running On Midinome
          - IF Playing Loop
            - **( Stop Loop Immediately )**
            - _Note: The metronome will continue but the loop will stop playing immediately_
          - IF Not Playing Loop
            - **( Clear Loop )**
        - IF Loop NOT Running On Midinome
        <!-- Functionality Can Go Here -->

  <!-- - COMMAND_BUTTON?
    - SINGLE_PRESS
    - DOUBLE_PRESS
    - HOLD -->

  - PLUS_BUTTON

    - SINGLE_PRESS

      - LIVE_MODE
        **( Increase to standard time or double time )**

      - CONFIG_MODE
        **( UP/Increment )**

      - TIME_SIGNATURE_MODE
        **( Selection Decrement )**

      - MANUAL_BPM_MODE
        **( Increase BPM By 1 )**

    - DOUBLE_PRESS
    <!-- Functionality Can Go Here -->
    - HOLD
      - MANUAL_BPM_MODE
        **( Increase BPM By 20 )**

  - MINUS_BUTTON

    - SINGLE_PRESS

      - LIVE_MODE
        **( Decrease to standard time or half time )**

      - CONFIG_MODE
        **( DOWN/Decrement )**

      - TIME_SIGNATURE_MODE
        **( Selection Decrement )**

      - MANUAL_BPM_MODE
        **( Decrease BPM By 1 )**

    - DOUBLE_PRESS
    <!-- Functionality Can Go Here -->

    - HOLD
      - MANUAL_BPM_MODE
        **( Increase BPM By 20 )**

## Program Event Loop
