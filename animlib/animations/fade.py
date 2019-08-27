from animlib.animations.animation import Animation, AnimationOut
from animlib.geometies.base import Base
from animlib.utils.colors import ColorComponent

import numpy as np

class FadeIn(Animation):

    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)

        self._targetStrokeAlphas = []
        self._targetFillAlphas = []

    def begin(self) -> int:
        ret = super().begin()
        
        self._targetStrokeAlphas = [o.getStrokeColor(ColorComponent.OPACITY) for o in self._targetObjects]
        self._targetFillAlphas = [o.getFillColor(ColorComponent.OPACITY) for o in self._targetObjects]

        [o.setFill(opacity=0.0) for o in self._animatedObjects]
        [o.setStroke(opacity=0.0) for o in self._animatedObjects]

        return ret

    def next(self) -> bool:
        """ Calculates and updates properies of animated objects and returns
            whether a next frame is available for the animation or not """
        if self._animCounter > self._animationLength():
            return False
        # if end is reached, clean up and return false
        if self._animCounter == self._animationLength():
            self.finish()
        else:
            # otherwise update properties of all animated objects
            for animatedObject, targetStrokeAlpha, targetFillAlpha in zip(self._animatedObjects, self._targetStrokeAlphas, self._targetFillAlphas):
                animatedObject.setStroke(opacity=self._easeVals[self._animCounter] * targetStrokeAlpha)
                animatedObject.setFill(opacity=self._easeVals[self._animCounter] * targetFillAlpha,)
        self._animCounter += 1
        return True


class FadeOut(FadeIn, AnimationOut):

    def begin(self) -> [Base]:
        ret = super().begin()

        [o.setFill(opacity=0.0) for o in self._targetObjects]
        [o.setStroke(opacity=0.0) for o in self._targetObjects]

        return ret
