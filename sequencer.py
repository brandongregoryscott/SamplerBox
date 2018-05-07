import rtmidi2
import datetime
import time
import random
from time import sleep


class MidiSequence:
    def __init__(self):
        self.events = []

class MidiEvent:
    def __init__(self, cmd, note, velocity, timestamp, sleeptime):
        self.cmd = cmd
        self.note = note
        self.velocity = velocity
        self.timestamp = timestamp
        self.sleeptime = sleeptime

    def play(self):
        print('Playing event')
        sleep(self.sleeptime.seconds + self.sleeptime.microseconds / 1000000.0)
        if self.cmd == NOTE_ON:
            mpk_mini.send_noteon(1, self.note, self.velocity)
        elif self.cmd == NOTE_OFF:
            mpk_mini.send_noteoff(1, self.note)


SRC_CMD_TOUCH = ['CMD Touch']
SRC_MPK_MINI = ['LPK25', 'MPKmini2', 'VMPK Output']

CIRCULAR_PADS, SQUARE_PADS, ALL_PADS = [], [], []
SEQUENCES = dict()
LED = {
    'RED': 79,
    'YELLOW': 63,
    'GREEN': 1,
    'OFF': 64
}
CHANNEL = 0
CURRENT_MODE = 63
RECORD_BUTTON = 116
RECORDING_MODE = 79
PLAY_MODE = 32
STANDBY_MODE = 1
SEQUENCE_PENDING_MODE = 63
RECORDING_SEQUENCE = MidiSequence()
NOTE_ON = 144
NOTE_OFF = 128

cmd_touch = rtmidi2.MidiOut()
cmd_touch.open_port(0)

mpk_mini = rtmidi2.MidiOut()
mpk_mini.open_port('SamplerBoxLoop')



def callback(src, msg, ts):
    global CURRENT_MODE
    global RECORDING_SEQUENCE
    cmd = msg[0]
    note = msg[1]
    if len(msg) > 2:
        velocity = msg[2]
    ts = datetime.datetime.now()
    print(src, msg, str(ts))
    if src in SRC_CMD_TOUCH:
        # (u'CMD Touch', [144, 108, 127], '2018-04-07 15:59:04')
        # MSG[0] IS ALWAYS 144
        # MSG[1] IS THE NOTE
        # MSG[2] IS THE VELOCITY - 127 IS ON, 0 IS OFF
        # 1-63 is green -> yellow
        # 64 is off
        # 65-79 is red
        if cmd == NOTE_ON and note == RECORD_BUTTON and velocity == 127:
            if CURRENT_MODE == STANDBY_MODE:
                set_record_mode(RECORDING_MODE)
            elif CURRENT_MODE == RECORDING_MODE:
                if len(RECORDING_SEQUENCE.events) > 0:
                    print('Finished recording sequence')
                    set_record_mode(SEQUENCE_PENDING_MODE)
                else:
                    print('No events recorded. Going back to standby')
                    set_record_mode(STANDBY_MODE)
            elif CURRENT_MODE == SEQUENCE_PENDING_MODE:
                print('Erasing sequence')
                RECORDING_SEQUENCE = MidiSequence()
                set_record_mode(STANDBY_MODE)
        if CURRENT_MODE == SEQUENCE_PENDING_MODE:
            if cmd == NOTE_ON and note in SQUARE_PADS and velocity == 127:
                print('Assigning sequence to {}'.format(note))
                SEQUENCES[note] = RECORDING_SEQUENCE
                cmd_touch.send_noteon(CHANNEL, note, LED['YELLOW'])
    if CURRENT_MODE == RECORDING_MODE and src in SRC_MPK_MINI:
        sleeptime = ts - ts
        if len(RECORDING_SEQUENCE.events) > 0:
            sleeptime = ts - RECORDING_SEQUENCE.events[-1].timestamp
        RECORDING_SEQUENCE.events.append(MidiEvent(cmd, note, velocity, ts, sleeptime))

                # cmd_touch.send_noteoff(0, note)
        # if cmd == CMD_TOUCH_NOTE_ON and note == RECORD_BUTTON and velocity == 0:

            # midi_out.send_noteon(0, msg[1], random.randint(0, 127))
            # for i in range(80, 85):
            #     sleep(0.5)
            #     cmd_touch.send_noteon(0, msg[1], i)


        # print("From cmd touch")
    # if msg[0] == 144:
    #     midi_out.send()
    # if src == 'nanoKONTROL2 SLIDER/KNOB':
    #     if msg[0] == 176 and msg[2] == 127:
    #         if msg[1] in [58, 59, 60, 46, 43, 44, 42, 41, 45]:


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


def flash_leds(pads, color, count=5):
    velocities = []
    channels = []
    for note in pads:
        velocities.append(color)
        channels.append(CHANNEL)
    for i in range(0, count):
        cmd_touch.send_noteon_many(channels, pads, velocities)
        sleep(0.3)
        cmd_touch.send_noteoff_many(channels, pads)
        sleep(0.3)


def set_record_mode(mode):
    global CURRENT_MODE
    CURRENT_MODE = mode
    # print('Setting current mode to {}'.format(CURRENT_MODE))
    cmd_touch.send_noteon(CHANNEL, RECORD_BUTTON, mode)


def initialize():
    initialize_pads()
    flash_leds(ALL_PADS, LED['YELLOW'], 2)
    set_record_mode(STANDBY_MODE)


initialize()
while True:
    for pad, sequence in SEQUENCES.items():
        for event in sequence.events:
            event.play()
