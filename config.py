AUDIO_DEVICE_ID = 6                   # change this number to use another soundcard
SAMPLES_DIR = "."                      # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
USE_SERIALPORT_MIDI = False             # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
USE_I2C_7SEGMENTDISPLAY = False         # Set to True to use a 7-segment display via I2C
USE_BUTTONS = False                     # Set to True to use momentary buttons (connected to RaspberryPi's GPIO pins) to change preset
MAX_POLYPHONY = 80                      # This can be set higher, but 80 is a safe value
IGNORE_PORTS = ['Midi Through', 'CMD Touch', 'IAC Driver CMD Touch', 'IAC Driver Processing'] # MIDI Ports to ignore input from
PANIC_KEY = 47 # Note to stop all playing sounds