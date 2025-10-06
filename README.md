# piano-to-keyboard
Converts MIDI notes to either an 88 key format or a 55 key format

Version 1.1  
Files: README.md, ptk88.py (88 key version), ptk55.py (55 key version)

Sustain = space key  
Notes A0 - B1 = Keys ctrl+1 - ctrl+t  (only in 88 key)  
Notes C2 - C7 = Keys 1 - m, with sharps being controlled by the shift key  
Notes C#7 - C8 = Keys ctrl+y - ctrl+j  (only in 88 key)

Requirements: Windows 11, Python 3.8+, MIDI device  
Installations:   
  &nbsp;&nbsp;&nbsp;&nbsp;Python (add python to PATH in installation)  
  &nbsp;&nbsp;&nbsp;&nbsp;Run in Command Prompt: pip install mido python-rtmidi pynput  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If installing python-rtmidi fails, install Visual C++ Build Tools  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Select Desktop development with C++ in the installer  

If you're using a program that only supports 55 key, then use the 55 key version so it doesn't get messed up.

In some virtual piano applications, the space key is used to toggle sheets instead of sustain, but it shouldn't impact performance.
