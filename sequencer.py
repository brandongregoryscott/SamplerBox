import rtmidi2
import datetime
import time
import random
from time import sleep
import json
from enums import LED, BUTTON, NOTE, MODE

class MidiSequence:
    def __init__(self):
        self.events = []
        self.playing = False

    def __str__(self):
        this = []
        for event in self.events:
            this.append(event.__dict__)
        return str(this)

class MidiEvent:
    def __init__(self, cmd, note, velocity, timestamp, sleeptime):
        self.cmd = cmd
        self.note = note
        self.velocity = velocity
        self.timestamp = timestamp
        self.sleeptime = sleeptime

    def play(self):
        sleep(self.sleeptime.seconds + self.sleeptime.microseconds / 1000000.0)
        if self.cmd == NOTE.On:
            mpk_mini.send_noteon(1, self.note, self.velocity)
        elif self.cmd == NOTE.Off:
            mpk_mini.send_noteoff(1, self.note)

    def __str__(self):
        return str(self.__dict__)

SRC_CMD_TOUCH = ['CMD Touch']
SRC_MPK_MINI = ['LPK25', 'MPKmini2', 'VMPK Output']

CIRCULAR_PADS, SQUARE_PADS, ALL_PADS = [], [], []
SEQUENCES = dict()

CHANNEL = 0
CURRENT_MODE = MODE.Standby
RECORDING_SEQUENCE = MidiSequence()


cmd_touch = rtmidi2.MidiOut()
cmd_touch.open_port(0)

mpk_mini = rtmidi2.MidiOut()
mpk_mini.open_port('SamplerBoxLoop')

def cmd_touch_handler(cmd, note, velocity, timestamp):
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    if cmd == NOTE.On and note == BUTTON.Record and velocity == 127:
        if CURRENT_MODE == MODE.Standby:
            set_record_mode(MODE.Record)
        elif CURRENT_MODE == MODE.Record:
            if len(RECORDING_SEQUENCE.events) > 0:
                print('Finished recording sequence')
                print(str(RECORDING_SEQUENCE))
                RECORDING_SEQUENCE.events[0].sleeptime = RECORDING_SEQUENCE.events[-1].sleeptime
                set_record_mode(MODE.Pending)
            else:
                print('No events recorded. Going back to standby')
                set_record_mode(MODE.Standby)
        elif CURRENT_MODE == MODE.Pending:
            print('Erasing sequence')
            RECORDING_SEQUENCE = MidiSequence()
            set_record_mode(MODE.Standby)
    if CURRENT_MODE == MODE.Pending:
        if cmd == NOTE.On and note in SQUARE_PADS and velocity == 127:
            print('Assigning sequence to {}'.format(note))
            SEQUENCES[note] = RECORDING_SEQUENCE
            cmd_touch.send_noteon(CHANNEL, note, LED.Yellow)
    if CURRENT_MODE == MODE.Standby:
        if cmd == NOTE.On and note in SQUARE_PADS and velocity == 127:
            if note in SEQUENCES.keys():
                set_sequence_status(note)


def mpk_mini_handler(cmd, note, velocity, timestamp):
    if CURRENT_MODE == MODE.Record:
        sleeptime = timestamp - timestamp
        if len(RECORDING_SEQUENCE.events) > 0:
            sleeptime = timestamp - RECORDING_SEQUENCE.events[-1].timestamp
        RECORDING_SEQUENCE.events.append(MidiEvent(cmd, note, velocity, timestamp, sleeptime))

def callback(src, msg, ts):
    cmd = msg[0]
    note = msg[1]
    velocity = msg[2] if len(msg) > 2 else 0
    timestamp = datetime.datetime.now()
    print(src, msg, str(timestamp))
    if src in SRC_CMD_TOUCH:
        cmd_touch_handler(cmd, note, velocity, timestamp)
    elif src in SRC_MPK_MINI:
        mpk_mini_handler(cmd, note, velocity, timestamp)

midi_in = rtmidi2.MidiInMulti().open_ports("*")
midi_in.callback = callback

def initialize_pads():
    global CIRCULAR_PADS
    global SQUARE_PADS
    global ALL_PADS
    CIRCULAR_PADS, SQUARE_PADS, ALL_PADS = [], [], []
    for pad in range(12, 19 + 1):
        CIRCULAR_PADS.append(pad)
    for pad in range(32, 116 + 1, 12):
        CIRCULAR_PADS.append(pad)
    for start in range(24, 108 + 1, 12):
        for pad in range(start, start + 8):
            SQUARE_PADS.append(pad)
    ALL_PADS = CIRCULAR_PADS + SQUARE_PADS


def flash_leds(pads, color, count=5, delay=0.3):
    velocities = []
    channels = []
    for note in pads:
        velocities.append(color)
        channels.append(CHANNEL)
    for i in range(0, count):
        cmd_touch.send_noteon_many(channels, pads, velocities)
        sleep(delay)
        cmd_touch.send_noteoff_many(channels, pads)
        sleep(delay)


def set_record_mode(mode):
    global CURRENT_MODE
    CURRENT_MODE = mode
    # print('Setting current mode to {}'.format(CURRENT_MODE))
    cmd_touch.send_noteon(CHANNEL, BUTTON.Record, mode)

def set_sequence_status(pad):
    SEQUENCES[pad].playing = not SEQUENCES[pad].playing
    if SEQUENCES[pad].playing:
        cmd_touch.send_noteon(CHANNEL, pad, LED.Green)
    else:
        cmd_touch.send_noteon(CHANNEL, pad, LED.Yellow)

def initialize():
    initialize_pads()
    flash_leds(ALL_PADS, LED.Green, 2)
    set_record_mode(MODE.Standby)


initialize()
while True:
    for pad, sequence in SEQUENCES.items():
        if sequence.playing:
            for event in sequence.events:
                event.play()
