from animlib.geometies.base import Base
from animlib.utils.points import convertToPoints, interpolateLinear, sliceBezier
import numpy as np

class Line(Base):
    def __init__(self, *args, **kwargs):
        # Make transparent unless otherwise specified
        if not any([k in kwargs.keys() for k in ["fillColor", "fill_color"]]):
            kwargs["fillColor"] = (0, 0, 0, 0)

        super().__init__(**kwargs)

        if len(args) >= 1:
            kwargs["start"] = args[0]
        if len(args) >= 2:
            kwargs["end"] = args[1]

        start = np.array((-100, 0)).reshape((1, 2))
        end = np.array((100, 0)).reshape((1, 2))

        for key in kwargs:
            arg = kwargs[key]
            if key in ["start", "Start"]:
                start = convertToPoints(arg)
            if key in ["end", "End"]:
                end = convertToPoints(arg)
        
        self.addPath()
        self.addPoint(interpolateLinear(start, end))
