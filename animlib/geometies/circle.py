from animlib.geometies.base import Base
from animlib.utils.points import convertToPoints

import numpy as np

class Circle(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._x = 0.0
        self._y = 0.0
        self._r = 100.0

        for key in kwargs:
            arg = kwargs[key]
            if key in ["x", "X"]:
                self._x = float(arg) 
            if key in ["y", "Y"]:
                self._y = float(arg) 
            if key in ["r", "R"]:
                self._r = float(arg)

        self._convertCircleToPoints()

    def _convertCircleToPoints(self):
        super().addPath()
        
        bezFac = 0.55

        start = convertToPoints((self._x-self._r, self._y))
        self.addPoint(start)
        a1 = convertToPoints((self._x-self._r, self._y-self._r*bezFac))
        a2 = convertToPoints((self._x-self._r*bezFac, self._y-self._r))
        end = convertToPoints((self._x, self._y-self._r))
        self.addPoint(np.concatenate((a1, a2, end), 0))
        start = end
        a1 = convertToPoints((self._x+self._r*bezFac, self._y-self._r))
        a2 = convertToPoints((self._x+self._r, self._y-self._r*bezFac))
        end = convertToPoints((self._x+self._r, self._y))
        self.addPoint(np.concatenate((a1, a2, end), 0))
        start = end
        a1 = convertToPoints((self._x+self._r, self._y+self._r*bezFac))
        a2 = convertToPoints((self._x+self._r*bezFac, self._y+self._r))
        end = convertToPoints((self._x, self._y+self._r))
        self.addPoint(np.concatenate((a1, a2, end), 0))
        start = end
        a1 = convertToPoints((self._x-self._r*bezFac, self._y+self._r))
        a2 = convertToPoints((self._x-self._r, self._y+self._r*bezFac))
        end = convertToPoints((self._x-self._r, self._y))
        self.addPoint(np.concatenate((a1, a2, end), 0))