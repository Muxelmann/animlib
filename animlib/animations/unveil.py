from animlib.animations.animation import Animation, AnimationOut
from animlib.geometies.base import Base

try:
    import cairo
except:
    import cairocffi as cairo
import numpy as np
from enum import Enum

class UnveilDirections(Enum):
    LEFT =          ( 1.0,  0.0,  1.0,  0.0)
    TOP_LEFT =      ( 1.0,  1.0,  1.0,  1.0)
    TOP =           ( 0.0,  1.0,  0.0,  1.0)
    TOP_RIGHT =     (-1.0,  1.0, -1.0,  1.0)
    RIGHT =         (-1.0,  0.0, -1.0,  0.0)
    BOTTOM_RIGHT =  (-1.0, -1.0, -1.0, -1.0)
    BOTTOM =        ( 0.0, -1.0,  0.0, -1.0)
    BOTTOM_LEFT =   ( 1.0, -1.0,  1.0, -1.0)

class Unveil(Animation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._unveilFrom = UnveilDirections.LEFT

        for key in kwargs.keys():
            arg = kwargs[key]
            if key in ["unveilFrom", "unveil_from"]:
                self._unveilFrom = arg if isinstance(arg, UnveilDirections) else UnveilDirections.LEFT

        self._targetFillColors = []
        self._targetStrokeColors = []
        self._outlines = []
        
    def begin(self) -> int:
        ret = super().begin()

        self._targetStrokeColors = [o.getStrokeColor() for o in self._targetObjects]
        self._targetFillColors = [o.getFillColor() for o in self._targetObjects]
        self._outlines = [o.getOutline().reshape((1, 4)) for o in self._targetObjects]
        maxStrokeOffset = np.max(np.array([o.getStrokeWidth() for o in self._targetObjects])).squeeze() / 2.0
        
        self._unveilStartStop = np.concatenate((
            np.min(np.concatenate(self._outlines, 0), 0)[:2],
            np.max(np.concatenate(self._outlines, 0), 0)[2:]
        ), 0)

        self._unveilStartStop *= np.array(self._unveilFrom.value)
        self._unveilStartStop += np.array(self._unveilFrom.value) * np.array((-1, -1, 1, 1)) * maxStrokeOffset
        self._unveilStartStop = self._unveilStartStop.reshape((2, 2))

        [o.setFill(opacity=0.0) for o in self._animatedObjects]
        [o.setStroke(opacity=0.0) for o in self._animatedObjects]

        return ret

    def next(self) -> bool:

        if self._animCounter > self._animationLength():
            return False

        if self._animCounter == self._animationLength():
            self.finish()
        else:
            for animatedObject, targetStrokeColor, targetFillColor in zip(self._animatedObjects, self._targetStrokeColors, self._targetFillColors):
                linearStrokeGradient = cairo.LinearGradient(
                    self._unveilStartStop[0, 0],
                    self._unveilStartStop[0, 1],
                    self._unveilStartStop[1, 0],
                    self._unveilStartStop[1, 1])
                linearStrokeGradient.add_color_stop_rgba(
                    self._easeVals[self._animCounter],
                    targetStrokeColor[0],
                    targetStrokeColor[1],
                    targetStrokeColor[2],
                    targetStrokeColor[3]
                )
                linearStrokeGradient.add_color_stop_rgba(
                    self._easeVals[self._animCounter],
                    targetStrokeColor[0],
                    targetStrokeColor[1],
                    targetStrokeColor[2],
                    0.0
                )
                animatedObject.setStroke(gradient=linearStrokeGradient)
                linearFillGradient = cairo.LinearGradient(
                    self._unveilStartStop[0, 0],
                    self._unveilStartStop[0, 1],
                    self._unveilStartStop[1, 0],
                    self._unveilStartStop[1, 1])
                linearFillGradient.add_color_stop_rgba(
                    self._easeVals[self._animCounter],
                    targetFillColor[0],
                    targetFillColor[1],
                    targetFillColor[2],
                    targetFillColor[3]
                )
                linearFillGradient.add_color_stop_rgba(
                    self._easeVals[self._animCounter],
                    targetFillColor[0],
                    targetFillColor[1],
                    targetFillColor[2],
                    0.0
                )
                animatedObject.setFill(gradient=linearFillGradient)

        self._animCounter += 1
        return True
    
class Hide(Unveil, AnimationOut):
    def finish(self):
        super().finish()
        [o.setFill(opacity=0.0) for o in self._targetObjects]
        [o.setStroke(opacity=0.0) for o in self._targetObjects]