from enum import IntEnum

# Enum to hold LED MIDI values
class LED(IntEnum):
    DimRed = int(1)
    Red = int(79)
    Yellow = int(63)
    Green = int(32)
    Off = int(64)

# Enum to hold modifier button representations
class BUTTON(IntEnum):
    Record = int(116)
    Edit = int(104)

# Enum to hold mode representations
class MODE(IntEnum):
    # Currently recording input from keyboard to build a sequence
    Record = LED.Red
    # No mode selected
    Standby = LED.DimRed
    # Sequence is pending and can be assigned to pads
    Pending = LED.Yellow

# Enum to hold on/off MIDI values
class NOTE(IntEnum):
    On = int(144)
    Off = int(128)