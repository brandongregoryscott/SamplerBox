import rtmidi2
import datetime
import time
from time import sleep
from enums import LED, NOTE, MODE, PAD, ARROW
import copy
from subprocess import Popen
import os
import thread


class MidiSequence:
    def __init__(self):
        self.events = []
        self.playing = False
        self.status = PAD.Unassigned

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

SRC_CMD_TOUCH = ['CMD Touch', 'IAC Driver CMD Touch']
SRC_MPK_MINI = ['LPK25', 'MPKmini2', 'VMPK Output']

CIRCULAR_PADS, SQUARE_PADS, ALL_PADS = [], [], []
SEQUENCES = dict()

CHANNEL = 0

RECORDING_SEQUENCE = MidiSequence()
SELECTED_SEQUENCES = set()


cmd_touch = rtmidi2.MidiOut()
# Check for physical cmd touch using get_in_ports()
if 'CMD Touch' in rtmidi2.get_in_ports():
    cmd_touch.open_port('CMD Touch')
else:
    # If the physical cmd touch pad is not present, we are emulating it
    # with a virtual midi port & Processing sketch to intercept signals
    pid = Popen(["/usr/local/bin/processing-java", "--sketch={}/{}".format(os.getcwd(), "VirtualCMDTouch"), "--run"])
    sleep(3)
    cmd_touch.open_port('IAC Driver Processing')

mpk_mini = rtmidi2.MidiOut()
mpk_mini.open_port('SamplerBoxLoop')


def record_button_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    if MODE.RECORD.Standby in CURRENT_MODE.values():
        set_current_mode(MODE.RECORD, MODE.RECORD.Record)
    elif MODE.RECORD.Record in CURRENT_MODE.values():
        if len(RECORDING_SEQUENCE.events) > 0:
            print('Finished recording sequence')
            print(str(RECORDING_SEQUENCE))
            RECORDING_SEQUENCE.events[0].sleeptime = RECORDING_SEQUENCE.events[-1].sleeptime
            set_current_mode(MODE.RECORD, MODE.RECORD.Pending)
        else:
            print('No events recorded. Going back to standby')
            set_current_mode(MODE.RECORD, MODE.RECORD.Standby)
    elif MODE.RECORD.Pending in CURRENT_MODE.values():
        print('Erasing sequence')
        RECORDING_SEQUENCE = MidiSequence()
        set_current_mode(MODE.RECORD, MODE.RECORD.Standby)


def edit_button_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    global CURRENT_MODE
    global SELECTED_SEQUENCES
    if MODE.EDIT.Standby in CURRENT_MODE.values():
        set_current_mode(MODE.EDIT, MODE.EDIT.Pitch)
    elif MODE.EDIT.Pitch in CURRENT_MODE.values():
        for sequence in SELECTED_SEQUENCES:
            flash_led(sequence, PAD.Off, count=1, delay=0, off=False)
        SELECTED_SEQUENCES.clear()
        set_current_mode(MODE.EDIT, MODE.EDIT.Standby)


def select_button_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    global CURRENT_MODE
    if MODE.SELECT.Select in CURRENT_MODE.values():
        set_current_mode(MODE.SELECT, MODE.SELECT.Standby)
    else:
        set_current_mode(MODE.SELECT, MODE.SELECT.Select)


def square_pad_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    if MODE.RECORD.Pending in CURRENT_MODE.values():
        print('Assigning sequence to {}'.format(note))
        SEQUENCES[note] = copy.deepcopy(RECORDING_SEQUENCE)
        set_pad_status(note, PAD.Off)
    elif MODE.SELECT.Select in CURRENT_MODE.values():
        if note in SEQUENCES.keys():
            if SEQUENCES[note].status == PAD.Selected:
                print('Unselecting sequence {}'.format(note))
                SELECTED_SEQUENCES.remove(note)
                set_pad_status(note, PAD.Off)
            else:
                print('Selecting sequence {}'.format(note))
                SELECTED_SEQUENCES.add(note)
                set_pad_status(note, PAD.Selected)
            print('Selected sequences: {}'.format(SELECTED_SEQUENCES))
        else:
            print('No sequence at pad {}'.format(note))
    # Commenting out the play/pause toggle until the selection is sorted out
    if MODE.RECORD.Standby in CURRENT_MODE.values() \
            and MODE.SELECT.Select not in CURRENT_MODE.values():
        if note in SEQUENCES.keys():
            if SEQUENCES[note].status == PAD.On:
                set_pad_status(note, PAD.Off)
            else:
                set_pad_status(note, PAD.On)


def arrow_pad_handler(cmd, note, velocity, timestamp):
    if velocity == 0:
        return
    global CURRENT_MODE
    if CURRENT_MODE[MODE.EDIT] == MODE.EDIT.Pitch:
        global SEQUENCES
        if note == ARROW.UP or note == ARROW.DOWN:
            flash_led(note, LED.DimOrange, count=2, delay=0.1, off=False)
            for pad in SELECTED_SEQUENCES:
                sequence = SEQUENCES.get(pad)
                flash_led(pad, PAD.Selected, count=2, delay=0.1, off=False)
                for event in sequence.events:
                    if note == ARROW.UP:
                        event.note += 1
                    else:
                        event.note -= 1


CURRENT_MODE = {
    MODE.RECORD: MODE.RECORD.Standby,
    MODE.EDIT: MODE.EDIT.Standby,
    MODE.SELECT: MODE.SELECT.Standby
}

BUTTON_SWITCH = {
    int(ARROW.UP): arrow_pad_handler,
    int(ARROW.DOWN): arrow_pad_handler,
    int(ARROW.LEFT): arrow_pad_handler,
    int(ARROW.RIGHT): arrow_pad_handler,
    int(MODE.RECORD): record_button_handler,
    int(MODE.EDIT): edit_button_handler,
    int(MODE.SELECT): select_button_handler
}


def cmd_touch_handler(cmd, note, velocity, timestamp):
    try:
        BUTTON_SWITCH[note](cmd, note, velocity, timestamp)
    except KeyError:
        # If the note is not in the button switch, it must be a square pad
        square_pad_handler(cmd, note, velocity, timestamp)


def mpk_mini_handler(cmd, note, velocity, timestamp):
    if MODE.RECORD.Record in CURRENT_MODE.values():
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


def flash_leds(pads, color, count=5, delay=0.3, off=True):
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
    if not off:
        cmd_touch.send_noteon_many(channels, pads, velocities)


# Private threaded method
def __flash_led(pad, color, count, delay, off):
    for i in range(0, count):
        cmd_touch.send_noteon(CHANNEL, pad, color)
        sleep(delay)
        cmd_touch.send_noteoff(CHANNEL, pad)
        sleep(delay)
    if not off:
        cmd_touch.send_noteon(CHANNEL, pad, color)


def flash_led(pad, color, count=5, delay=0.3, off=True):
    thread.start_new_thread(__flash_led, (pad, color, count, delay, off))


def set_current_mode(mode, status):
    global CURRENT_MODE
    CURRENT_MODE[mode] = status
    cmd_touch.send_noteon(CHANNEL, mode, status)


def set_pad_status(pad, status):
    global SEQUENCES
    cmd_touch.send_noteon(CHANNEL, pad, status)
    if status == PAD.On:
        SEQUENCES[pad].playing = True
    elif status == PAD.Off:
        SEQUENCES[pad].playing = False
    SEQUENCES[pad].status = status


def initialize():
    initialize_pads()
    # Processing sketch doesn't seem to handle send_noteon_many very well
    # So we'll only flash the LEDs with the physical controller
    if 'CMD Touch' in rtmidi2.get_in_ports():
        flash_leds(ALL_PADS, LED.Green, 2)
    set_current_mode(MODE.RECORD, MODE.RECORD.Standby)
    set_current_mode(MODE.EDIT, MODE.EDIT.Standby)
    set_current_mode(MODE.SELECT, MODE.SELECT.Standby)
    set_current_mode(ARROW.UP, LED.DimOrange)
    set_current_mode(ARROW.DOWN, LED.DimOrange)
    set_current_mode(ARROW.LEFT, LED.DimOrange)
    set_current_mode(ARROW.RIGHT, LED.DimOrange)


initialize()
while True:
    for pad, sequence in SEQUENCES.items():
        if sequence.playing:
            for event in sequence.events:
                event.play()
