# novation-midi-controller

Thin MIDI wrapper for LAUNCHPAD PRO mk2 user.
This is a python script to map MIDI input values to macros. (like a midi-to-macro)

support only mk2.

See documents.
- [Mido](https://mido.readthedocs.io/en/latest/index.html)
- [Programmers Reference](https://downloads.novationmusic.com/novation/launchpad-mk2/launchpad-pro)

## usage
Simple usage.

``` python
# custom macros
def callback(msg):
    if msg.type == 'note_on':
        print(f"note on: {msg.note}, velocity={msg.velocity}")
    elif msg.type == 'cc':
        print(f"cc on: {msg.note}, velocity={msg.velocity}")

if __name__ == '__main__':
    device = LaunchPadProMk2(mode="STANDALONE")
    device.open(callback=callback)
```