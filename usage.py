#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import itertools
import time
import sys

from launchpad import LaunchPadProMk2

def callback(msg):
    if msg.type == 'sysex':
        print('sysex:', msg.data)
    elif msg.type == 'note_on':
        print(f"note on: {msg.note}, velocity={msg.velocity}")
    elif msg.type == 'cc':
        print(f"cc on: {msg.note}, velocity={msg.velocity}")
    # NOTE: LAUNCHPAD doesn't use 'note_off'
    # elif msg.type == 'note_off':
    #     print(msg)


if __name__ == '__main__':
    device = LaunchPadProMk2(mode="STANDALONE")
    device.open(callback=callback)
    # device.change_layout("note")
    # device.change_layout("drum")
    # device.change_layout("fader")
    device.change_layout("programmer")

    # Operate LED with sysex
    with open('led.csv') as f:
        led_csv = csv.reader(f)
        leds = [list(map(int, r)) for r in led_csv]
        leds = list(itertools.chain.from_iterable(leds[1:]))
        device.set_lit(colores=leds)
        time.sleep(0.3)
    device.column_lit(0, colores=[12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
    time.sleep(0.3)
    device.row_lit(0, colores=[12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
    time.sleep(0.3)
    device.all_lit(color=6)
    time.sleep(0.3)

    # Operate LED with note
    device.all_on()
    time.sleep(0.3)
    device.all_off()

    # Wait for exit
    exit = lambda: [device.close(), sys.exit(0)]
    while True:
        try:
            keys = input("Press Ctrl+C to exit or enter quit.")
        except KeyboardInterrupt:
            exit()
        if keys == 'quit' or keys == "q":
            exit()