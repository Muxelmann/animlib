from animlib.geometies.base import Base
from animlib.utils.points import convertToPoints, interpolateLinear

class Rect(Base):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._x = 0.0
        self._y = 0.0
        self._w = 0.0
        self._h = 0.0

        for key in kwargs:
            arg = kwargs[key]
            if key in ["x", "X"]:
                self._x = float(arg) 
            if key in ["y", "Y"]:
                self._y = float(arg) 
            if key in ["w", "W"]:
                self._w = float(arg) 
            if key in ["h", "H"]:
                self._h = float(arg)

        self._convertRectToPoints()
        
    def _convertRectToPoints(self):
        super().addPath()
        start = convertToPoints((self._x, self._y))
        self.addPoint(start)
        end = convertToPoints((self._x+self._w, self._y))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((self._x+self._w, self._y+self._h))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((self._x, self._y+self._h))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((self._x, self._y))
        self.addPoint(interpolateLinear(start, end)[1:,:])