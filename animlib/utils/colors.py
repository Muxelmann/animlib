import numpy as np
from enum import Enum

def convertToColor(val) -> np.ndarray:
    """
    Converts `val` to a numpy RGBA-color `1x4` array
    """

    if isinstance(val, ColorMap):
        val = val.value.lower()

    if isinstance(val, str):
        if val[0] == "#": # if hex value
            val = val[1:]
            if len(val) == 6: # if RGB (without A)
                val = np.array([int(val[i:i+2], 16)/ 255 for i in (0, 2, 4)] + [1.0])
            elif len(val) == 8: # if RGBA
                val = np.array([int(val[i:i+2], 16)/ 255 for i in (0, 2, 4, 6)])
    elif isinstance(val, (list, tuple)):
        val = np.array(val)
    
    if isinstance(val, np.ndarray):
        return val
    
    return np.array((1.0, 0, 0, 1.0))

class ColorComponent(Enum):
    R = 0
    G = 1
    B = 2
    # A = 3
    OPACITY = 3 # i.e. alpha value

class ColorMap(Enum):
    DARK_BLUE = "#236B8E"
    DARK_BROWN = "#8B4513"
    LIGHT_BROWN = "#CD853F"
    BLUE_E = "#1C758A"
    BLUE_D = "#29ABCA"
    BLUE_C = "#58C4DD"
    BLUE_B = "#9CDCEB"
    BLUE_A = "#C7E9F1"
    TEAL_E = "#49A88F"
    TEAL_D = "#55C1A7"
    TEAL_C = "#5CD0B3"
    TEAL_B = "#76DDC0"
    TEAL_A = "#ACEAD7"
    GREEN_E = "#699C52"
    GREEN_D = "#77B05D"
    GREEN_C = "#83C167"
    GREEN_B = "#A6CF8C"
    GREEN_A = "#C9E2AE"
    YELLOW_E = "#E8C11C"
    YELLOW_D = "#F4D345"
    YELLOW_C = "#FFFF00"
    YELLOW_B = "#FFEA94"
    YELLOW_A = "#FFF1B6"
    GOLD_E = "#C78D46"
    GOLD_D = "#E1A158"
    GOLD_C = "#F0AC5F"
    GOLD_B = "#F9B775"
    GOLD_A = "#F7C797"
    RED_E = "#CF5044"
    RED_D = "#E65A4C"
    RED_C = "#FC6255"
    RED_B = "#FF8080"
    RED_A = "#F7A1A3"
    MAROON_E = "#94424F"
    MAROON_D = "#A24D61"
    MAROON_C = "#C55F73"
    MAROON_B = "#EC92AB"
    MAROON_A = "#ECABC1"
    PURPLE_E = "#644172"
    PURPLE_D = "#715582"
    PURPLE_C = "#9A72AC"
    PURPLE_B = "#B189C6"
    PURPLE_A = "#CAA3E8"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    LIGHT_GRAY = "#BBBBBB"
    LIGHT_GREY = "#BBBBBB"
    GRAY = "#888888"
    GREY = "#888888"
    DARK_GREY = "#444444"
    DARK_GRAY = "#444444"
    DARKER_GREY = "#222222"
    DARKER_GRAY = "#222222"
    GREY_BROWN = "#736357"
    PINK = "#D147BD"
    LIGHT_PINK = "#DC75CD"
    GREEN_SCREEN = "#00FF00"
    ORANGE = "#FF862F"
    TRANSPARENT = "#FFFFFF00"
