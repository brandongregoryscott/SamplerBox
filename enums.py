from enum import Enum

# Enum to hold LED MIDI values
class LED(Enum):
    Red = 79
    Yellow = 63
    Green = 32
    Off = 64, 0

# Enum to hold modifier button representations
class BUTTON(Enum):
    Record = 116
    Edit = 104

# Enum to hold mode representations
class MODE(Enum):
    # Currently recording input from keyboard to build a sequence
    Record = 79
    # No mode selected
    Standby = 1
    # Sequence is pending and can be assigned to pads
    Pending = 63

# Enum to hold on/off MIDI values
class NOTE(Enum):
    On = 144
    Off = 128