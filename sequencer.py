import rtmidi2
import datetime
import time
from time import sleep
from enums import LED, NOTE, MODE
import copy

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

RECORDING_SEQUENCE = MidiSequence()

cmd_touch = rtmidi2.MidiOut()
cmd_touch.open_port(1)

mpk_mini = rtmidi2.MidiOut()
mpk_mini.open_port('SamplerBoxLoop')

def record_button_handler(cmd, note, velocity, timestamp):
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    if CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Standby:
        set_current_mode(MODE.RECORD, MODE.RECORD.Record)
    elif CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Record:
        if len(RECORDING_SEQUENCE.events) > 0:
            print('Finished recording sequence')
            print(str(RECORDING_SEQUENCE))
            RECORDING_SEQUENCE.events[0].sleeptime = RECORDING_SEQUENCE.events[-1].sleeptime
            set_current_mode(MODE.RECORD, MODE.RECORD.Pending)
        else:
            print('No events recorded. Going back to standby')
            set_current_mode(MODE.RECORD, MODE.RECORD.Standby)
    elif CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Pending:
        print('Erasing sequence')
        RECORDING_SEQUENCE = MidiSequence()
        set_current_mode(MODE.RECORD, MODE.RECORD.Standby)

def edit_button_handler(cmd, note, velocity, timestamp):
    print("In edit button handler: {} {} {} {}".format(cmd, note, velocity, timestamp))

def select_button_handler(cmd, note, velocity, timestamp):
    print("In select button handler: {} {} {} {}".format(cmd, note, velocity, timestamp))

def square_pad_handler(cmd, note, velocity, timestamp):
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    if CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Pending:
        print('Assigning sequence to {}'.format(note))
        SEQUENCES[note] = copy.deepcopy(RECORDING_SEQUENCE)
        cmd_touch.send_noteon(CHANNEL, note, LED.Yellow)
    if CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Standby:
        if note in SEQUENCES.keys():
            set_sequence_status(note)

CURRENT_MODE = {
    int(MODE.RECORD): MODE.RECORD.Standby,
    int(MODE.EDIT): MODE.RECORD.Standby,
    int(MODE.SELECT): MODE.SELECT.Standby
}

BUTTON_SWITCH = {
    int(MODE.RECORD): record_button_handler,
    int(MODE.EDIT): edit_button_handler,
    int(MODE.SELECT): select_button_handler
}

def cmd_touch_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    try:
        BUTTON_SWITCH[note](cmd, note, velocity, timestamp)
    except KeyError:
        # If the note is not in the button switch, it must be a square pad
        square_pad_handler(cmd, note, velocity, timestamp)


def mpk_mini_handler(cmd, note, velocity, timestamp):
    if CURRENT_MODE[MODE.RECORD] == MODE.RECORD.Record:
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


def set_current_mode(button, mode):
    global CURRENT_MODE
    CURRENT_MODE[button] = mode
    cmd_touch.send_noteon(CHANNEL, button, mode)

def set_sequence_status(pad):
    SEQUENCES[pad].playing = not SEQUENCES[pad].playing
    if SEQUENCES[pad].playing:
        cmd_touch.send_noteon(CHANNEL, pad, LED.Green)
    else:
        cmd_touch.send_noteon(CHANNEL, pad, LED.Yellow)

def initialize():
    initialize_pads()
    flash_leds(ALL_PADS, LED.Green, 2)
    set_current_mode(MODE.RECORD, MODE.RECORD.Standby)
    set_current_mode(MODE.EDIT, MODE.EDIT.Standby)
    set_current_mode(MODE.SELECT, MODE.SELECT.Standby)


initialize()
while True:
    for pad, sequence in SEQUENCES.items():
        if sequence.playing:
            for event in sequence.events:
                event.play()
