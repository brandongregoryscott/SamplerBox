from enum import IntEnum

# Enum to hold LED MIDI values
class LED(IntEnum):
    DimRed = int(1)
    Red = int(79)
    Yellow = int(63)
    Green = int(32)
    Off = int(64)

class RECORD:
    def __init__(self):
        self.Standby = LED.DimRed
        # Currently recording input from keyboard to build a sequence
        self.Record = LED.Red
        # Sequence is pending and can be assigned to pads
        self.Pending = LED.Yellow

    def __trunc__(self):
        # Returns the integer representation of the mode button
        return int(116)

class EDIT:
    def __init__(self):
        self.Standby = LED.Yellow

    def __trunc__(self):
        # Returns the integer representation of the mode button
        return int(104)

# Enum to hold mode representations
class MODE:
    RECORD = RECORD()
    EDIT = EDIT()

# Enum to hold on/off MIDI values
class NOTE(IntEnum):
    On = int(144)
    Off = int(128)