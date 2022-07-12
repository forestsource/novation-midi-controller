import mido
import time
import sys
import csv
import itertools

COLORS = {
    "black": 0, #000000
    "dark_gray": 1,#1C1C1C
    "white": 4,#FCFCFC
    "venetian_red": 5,#FF4D47
    "blood_red": 6, #5A0100
    "smokey_black": 7, #190000

    "rajah": 8, #FFBD62
    "mystic_red": 9, #FF5600
    "seal_brown": 10, #5A1D00
    "zinnwaldite_brown": 11, #231800
    "yellow_sun": 12, #FDFD21
    "dark_bronze": 13, #585800
    "smokey_black": 14, #181800

}

class LaunchPadProMk2:
    MODE = {
        "ABLETON": {
            "in": "Launchpad Pro",
            "out": "Launchpad Pro"
        },
        "STANDALONE": {
            "in": "MIDIIN2 (Launchpad Pro)",
            "out": "MIDIOUT2 (Launchpad Pro)"
        },
        "HARDWARE": {
            "in": "MIDIIN3 (Launchpad Pro)",
            "out": "MIDIOUT3 (Launchpad Pro)"
        }
    }
    sleep_time = 1

    def __init__(self, mode="STANDALONE"):
        midi_outputs = mido.get_output_names()
        midi_inputs = mido.get_input_names()
        self.MODE[mode]
        input_port = [x for x in midi_inputs if (self.MODE[mode]["in"] in x)]
        output_port = [x for x in midi_outputs if (self.MODE[mode]["out"] in x)]

        # validation
        if len(input_port) >= 2:
            print("Too many Launchpad Pro(input) exists. Only support 1")
            return
        if len(output_port) >= 2:
            print("Too many Launchpad Pro(output) exists. Only support 1")
            return
        if not len(input_port) == 1:
            print("Launchpad Pro(input)is not exist.")
            return
        if not len(output_port) == 1:
            print("Launchpad Pro(output) is not exist.")
            return
        self._input_port_name = input_port[0]
        self._output_port_name = output_port[0]

    def open(self, callback=None):
        self.input = mido.open_input(self._input_port_name)
        self.output = mido.open_output(self._output_port_name)
        self.input.callback = callback or self.default_msg_handle

    def close(self):
        self.input.close()
        self.output.close()

    def change_layout(self, layout_name):
        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 44])
        if layout_name == "note":
            msg.data += [0]
        elif layout_name == "drum":
            msg.data += [1]
        elif layout_name == "fader":
            msg.data += [2]
        elif layout_name == "programmer":
            msg.data += [3]
        self.output.send(msg)
        time.sleep(LaunchPadProMk2.sleep_time)

    def column_lit(self, column, color=[1]):
        if len(color) > 10:
            print(" *Warning* Column max is 10")
            color = color[0:9]

        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 12, column])
        msg.data += color
        self.output.send(msg)
        time.sleep(LaunchPadProMk2.sleep_time)

    def row_lit(self, column, color=[1]):
        if len(color) > 10:
            print(" *Warning* Row max is 10")
            color = color[0:9]

        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 12, column])
        msg.data += color
        self.output.send(msg)
        time.sleep(LaunchPadProMk2.sleep_time)

    def all_lit(self, color=[1]):
        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 14])
        msg.data += color
        self.output.send(msg)
        time.sleep(LaunchPadProMk2.sleep_time)

    def set_lit(self, colors=[1]):
        if len(colors) >= 97:
            print(f"current color length is {len(colors)}. Max color length is 97")
            colors = colors[:96]
        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 14])
        msg.data += colors
        self.output.send(msg)
        time.sleep(LaunchPadProMk2.sleep_time)

    def default_msg_handle(self, msg):
        print("call handle", msg)

def main():
    device = LaunchPadProMk2(mode="STANDALONE")
    device.open()
    # device.change_layout("note")
    # device.change_layout("drum")
    # device.change_layout("fader")
    with open('led.csv') as f:
        led_csv = csv.reader(f)
        leds = [list(map(int, r)) for r in led_csv]
        leds = list(itertools.chain.from_iterable(leds[1:]))
        device.change_layout("programmer")
        device.all_lit(color=[6])
        device.set_lit(colors=leds)
        # device.column_lit(0, color=[12, 12, 12, 12, 12, 12, 12, 12, 12, 12])

    # wait for exit
    exit = lambda: [device.close(), sys.exit(0)]
    while True:
        try:
            keys = input("Press Ctrl+C to exit or enter quit.")
        except KeyboardInterrupt:
            exit()
        if keys == 'quit' or keys == "q":
            exit()

main()