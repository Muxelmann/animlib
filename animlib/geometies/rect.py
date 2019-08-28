from animlib.geometies.base import Base
from animlib.utils.points import convertToPoints, interpolateLinear

class Rect(Base):
    
    def __init__(self, *args, **kwargs):
        assert len(args) == 0 or len(args) == 4, "either pass 4 arguments for x, y, w, h or no unnamed arguments"
        super().__init__(**kwargs)

        self._x = args[0] if len(args) > 0 else 0.0 
        self._y = args[1] if len(args) > 1 else 0.0
        self._w = args[2] if len(args) > 2 else 1.0
        self._h = args[3] if len(args) > 3 else 1.0

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