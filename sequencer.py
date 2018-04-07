import rtmidi2
import datetime

def callback(src, msg, ts):
    print(src, msg, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
midi_in = rtmidi2.MidiIn()
midi_in.callback = callback
midi_in.open_port(0)
