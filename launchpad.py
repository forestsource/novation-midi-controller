#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thin MIDI wrapper for LAUNCHPAD PRO mk2 user.
This is a python script to map MIDI input values to macros.
(like a midi-to-macro)
"""

import mido
import sys
from logging import getLogger

import coloredlogs


class LaunchPadProMk2:
    """LaunchPadProMk2

    Attributes:
        mode ([str]): Default is 'STANDALONE'.
            If you use maintain of macros, use 'STANDALONE'.
            For details, see 'programmers reference guide'.
        logger ([logger]): your logger.
        debug ([boolean]): debug mode.
    """
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

    def __init__(self, mode="STANDALONE", logger=None, debug=False):
        if debug:
            logger = getLogger(__name__)
            coloredlogs.install(level='DEBUG', logger=logger)
        if not logger:
            self.logger = getLogger(__name__)
            coloredlogs.install(level='INFO', logger=self.logger)
        midi_outputs = mido.get_output_names()
        midi_inputs = mido.get_input_names()
        self.MODE[mode]
        input_port = [x for x in midi_inputs if (self.MODE[mode]["in"] in x)]
        output_port = [x for x in midi_outputs if (
            self.MODE[mode]["out"] in x)]

        # validation
        if len(input_port) >= 2:
            self.logger.critical(
                "Too many Launchpad Pro(input) exists. Only support 1")
            sys.exit()
        if len(output_port) >= 2:
            self.logger.critical(
                "Too many Launchpad Pro(output) exists. Only support 1")
            sys.exit()
        if not len(input_port) == 1:
            self.logger.critical("Launchpad Pro(input)is not exist.")
            sys.exit()
        if not len(output_port) == 1:
            self.logger.critical("Launchpad Pro(output) is not exist.")
            sys.exit()
        self._input_port_name = input_port[0]
        self._output_port_name = output_port[0]

    def open(self, callback=None):
        """open midi port

        Args:
            callback ([function]): Your macro function.
        """
        self.input = mido.open_input(self._input_port_name, callback=callback)
        self.output = mido.open_output(self._output_port_name)
        self.input.callback = callback or self.default_msg_handle

    def close(self):
        """close midi port
        """
        self.output.reset()
        self.output.panic()
        self.input.close()
        self.output.close()

    def change_layout(self, layout_name):
        """change layout

        Args:
            layout_name ([str]): If you use maintain of macros, use 'programmer'.
                                 For details, see 'programmers reference guide'.
        """
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

    def column_lit(self, column, colores=[1]):
        """lit a column

        Args:
            column ([int]): Column number.
            colores ([int]): Color numberes.(left to right)
                             See 'Color' section in 'programmers reference guide'.
        """
        if len(colores) > 10:
            self.logger.warning("Column max is 10")
            colores = colores[0:9]

        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 12, column])
        msg.data += colores
        self.output.send(msg)

    def row_lit(self, row, colores=[1]):
        """lit a row

        Args:
            row ([int]): Row number.
            colores ([int]): Color numberes.(bottom to up)
                             See 'Color' section in 'programmers reference guide'.
        """
        if len(colores) > 10:
            self.logger.warning("Row max is 10")
            colores = colores[0:9]

        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 13, row])
        msg.data += colores
        self.output.send(msg)

    def all_lit(self, color=[1]):
        """lit solid color all pads

        Args:
            color (int): Color number.
                         See 'Color' and 'Layout' section in 'programmers reference guide'.
        """
        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 14])
        msg.data += [color]
        self.output.send(msg)

    def set_lit(self, colores=[1]):
        """lit all pads

        Args:
            colores (int): Color numberes.
                           See 'Color' and 'Layout' section in 'programmers reference guide'.
        """
        if len(colores) >= 97:
            self.logger.warning(
                f"current color length is {len(colores)}. Max color length is 97")
            colores = colores[:96]
        msg = mido.Message('sysex', data=[0, 32, 41, 2, 16, 14])
        msg.data += colores
        self.output.send(msg)

    def all_on(self, channel=1):
        """lit solid color all pads

        Args:
            channel (int): Channel number. (1~16)
        """
        if not (1 <= channel <= 15):
            self.logger.error(
                f"channel {channel} is invalid. (select from 1~16)")
        channel -= 1
        for i in range(1, 99):
            msg = mido.Message('note_on', channel=channel,
                               note=i, velocity=127)
            self.output.send(msg)

    def all_off(self, channel=1):
        """unlit all pads

        Args:
            channel (int): Channel number. (1~16)
        """
        if not (1 <= channel <= 15):
            self.logger.error(
                f"channel {channel} is invalid. (select from 1~16)")
        channel -= 1
        for i in range(1, 99):
            msg = mido.Message('note_off', channel=channel, note=i)
            self.output.send(msg)

    def default_msg_handle(self, msg):
        """default callback handler

        Args:
            msg (Message): mido 'Message' object. For details, see Mido document.
        """
        self.logger.debug("Recive msg: ", msg)
