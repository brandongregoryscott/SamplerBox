from enum import IntEnum

# Enum to hold LED MIDI values
class LED(IntEnum):
    Off = int(0)
    DimRed = int(1)
    Red = int(2)
    BrightRed = int(3)
    DimGreen = int(16)
    Green = int(32)
    BrightGreen = int(48)
    DimYellow = int(17)
    Yellow = int(34)
    BrightYellow = int(51)
    DimOrange = int(18)
    RedOrange = int(19)
    Orange = int(35)
    DimGreenYellow = int(33)
    GreenYellow = int(49)
    YellowGreen = int(50)



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
        self.Standby = LED.DimYellow

    def __trunc__(self):
        # Returns the integer representation of the mode button
        return int(104)

class SELECT:
    def __init__(self):
        self.Standby = LED.DimGreen
        self.Select = LED.DimGreenYellow

    def __trunc__(self):
        # Returns the integer representation of the mode button
        return int(92)

# Enum to hold mode representations
class MODE:
    RECORD = RECORD()
    EDIT = EDIT()
    SELECT = SELECT()

# Enum to hold on/off MIDI values
class NOTE(IntEnum):
    On = int(144)
    Off = int(128)