#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# 
# You may not use this file except in compliance with the terms and conditions 
# set forth in the accompanying LICENSE.TXT file.
#
# THESE MATERIALS ARE PROVIDED ON AN "AS IS" BASIS. AMAZON SPECIFICALLY DISCLAIMS, WITH 
# RESPECT TO THESE MATERIALS, ALL WARRANTIES, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

import os
import sys
import time
import logging
import threading
import random

from agt import AlexaGadget

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2.motor import OUTPUT_B, OUTPUT_C, LargeMotor

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
logger = logging.getLogger(__name__)


class MindstormsGadget(AlexaGadget):
    """
    A Mindstorms gadget that performs movement in sync with music tempo.
    """

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.left_motor = LargeMotor(OUTPUT_B)
        self.right_motor = LargeMotor(OUTPUT_C)

        # Gadget states
        self.bpm = 0
        self.trigger_bpm = "off"

    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param friendly_name: the friendly name of the gadget that has connected to the echo device
        """
        self.leds.set_color("LEFT", "GREEN")
        self.leds.set_color("RIGHT", "GREEN")
        logger.info("{} connected to Echo device".format(self.friendly_name))

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param friendly_name: the friendly name of the gadget that has disconnected from the echo device
        """
        self.leds.set_color("LEFT", "BLACK")
        self.leds.set_color("RIGHT", "BLACK")
        logger.info("{} disconnected from Echo device".format(self.friendly_name))

    def on_alexa_gadget_musicdata_tempo(self, directive):
        """
        Provides the music tempo of the song currently playing on the Echo device.
        :param directive: the music data directive containing the beat per minute value
        """
        tempo_data = directive.payload.tempoData
        for tempo in tempo_data:

            print("tempo value: {}".format(tempo.value), file=sys.stderr)
            if tempo.value > 0:
                # dance pose
                self.right_motor.run_timed(speed_sp=750, time_sp=2500)
                self.left_motor.run_timed(speed_sp=-750, time_sp=2500)
                self.leds.set_color("LEFT", "GREEN")
                self.leds.set_color("RIGHT", "GREEN")
                time.sleep(3)
                # starts the dance loop
                self.trigger_bpm = "on"
                threading.Thread(target=self._dance_loop, args=(tempo.value,)).start()

            elif tempo.value == 0:
                # stops the dance loop
                self.trigger_bpm = "off"
                self.leds.set_color("LEFT", "BLACK")
                self.leds.set_color("RIGHT", "BLACK")

    def _dance_loop(self, bpm):
        """
        Perform motor movement in sync with the beat per minute value from tempo data.
        :param bpm: beat per minute from AGT
        """
        color_list = ["GREEN", "RED", "AMBER", "YELLOW"]
        led_color = random.choice(color_list)
        motor_speed = 400
        milli_per_beat = min(1000, (round(60000 / bpm)) * 0.65)
        print("Adjusted milli_per_beat: {}".format(milli_per_beat), file=sys.stderr)
        while self.trigger_bpm == "on":

            # Alternate led color and motor direction
            led_color = "BLACK" if led_color != "BLACK" else random.choice(color_list)
            motor_speed = -motor_speed

            self.leds.set_color("LEFT", led_color)
            self.leds.set_color("RIGHT", led_color)
            self.right_motor.run_timed(speed_sp=motor_speed, time_sp=150)
            self.left_motor.run_timed(speed_sp=-motor_speed, time_sp=150)
            time.sleep(milli_per_beat / 1000)

        print("Exiting BPM process.", file=sys.stderr)


if __name__ == '__main__':

    gadget = MindstormsGadget()

    # Set LCD font and turn off blinking green LEDs
    os.system('setfont Lat7-Terminus12x6')
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")

    # Startup sequence 
    gadget.sound.play_song((('C4', 'e'), ('D4', 'e'), ('E5', 'q')))
    gadget.leds.set_color("LEFT", "GREEN")
    gadget.leds.set_color("RIGHT", "GREEN")

    # Gadget main entry point
    gadget.main()

    # Shutdown sequence
    gadget.sound.play_song((('E5', 'e'), ('C4', 'e')))
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")
