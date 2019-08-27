from animlib.geometies.base import Base
from animlib.utils.colors import ColorComponent
from enum import Enum, unique
import numpy as np
import sys
try:
    import cairo
except:
    import cairocffi as cairo

class EaseFun():
    def __init__(self, fun):
        self._fun = fun

    def __call__(self, *args, **kwargs):
        return self._fun(*args, **kwargs)

@unique
class Ease(Enum):
    """
    Defines a set of easing functions for a percentage (p) of the animation
    
    Value can be compared like any enum, but when called, easing function is executed. E.g:\n
    `Ease.LINEAR == Ease.OUT_QUAD` returns `False`\n
    `Ease.OUT_QUAD == Ease.OUT_QUAD` returns `True`\n
    `Ease.LINEAR(0.5)` returns `0.5`\n
    `Ease.OUT_QUAD(0.5)` returns `0.25`
    """
    LINEAR =         EaseFun(lambda p: p)
    IN_QUAD =        EaseFun(lambda p: p*p)
    OUT_QUAD =       EaseFun(lambda p: p*(2-p))
    IN_OUT_QUAD =    EaseFun(lambda p: 2*p*p if p < 0.5 else (4-2*p)*p-1)
    IN_CUBIC =       EaseFun(lambda p: p*p*p)
    OUT_CUBIC =      EaseFun(lambda p: p*(p*(+-3*p)+3))
    IN_OUT_CUBIC =   EaseFun(lambda p: 4*p*p*p if p < 0.5 else p*(p*(p*4-12)+12)-3)
    IN_QUART =       EaseFun(lambda p: p*p*p*p)
    OUT_QUART =      EaseFun(lambda p: p*(p*(p*(4-p)-6)+4))
    IN_OUT_QUART =   EaseFun(lambda p: 8*p*p*p*p if p < 0.5 else p*(p*(p*(32-8*p)-48)+32)-7)
    # experimental using order (o): may be slow
    IN_ORDER =       EaseFun(lambda p, o: p**o)
    OUT_ORDER =      EaseFun(lambda p, o: 1-abs((p-1)**o))
    IN_OUT_ORDER =   EaseFun(lambda p, o: p*(2*p)**(o-1) if p < 0.5 else 1-abs((p-1)*(2*p-2)**(o-1)))
    # TODO: implement sine, circ, elastic, expo, back and bounce (see https://easings.net/)

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

class Animation:
    def __init__(self, *args, **kwargs):
        
        if len(args) > 0:
            kwargs.update({"end": args})

        self._targetObjects = []
        self._animatedObjects = []
        self._animTime = 1.0
        self._fps = 60.0
        self._easeFun = Ease.IN_OUT_QUAD

        for key in kwargs.keys():
            arg = kwargs[key]
            if key in ["start"]:
                if isinstance(arg, (list, tuple)):
                    if not all([isinstance(o, Base) for o in arg]):
                        raise Exception("all animated objects must be Base objects")    
                elif isinstance(arg, Base):
                    arg = [arg]
                else:
                    raise Exception("accepts only type Base or list(Base)")
                self._animatedObjects = arg
            if key in ["end", "to"]:
                if isinstance(arg, (list, tuple)):
                    if not all([isinstance(o, Base) for o in arg]):
                        raise Exception("all animated objects must be Base objects")    
                elif isinstance(arg, Base):
                    arg = [arg]
                else:
                    raise Exception("accepts only type Base or list(Base)")
                self._targetObjects = arg
            if key in ["animTime", "anim_time", "duration", "Duration"]:
                self._animTime = float(arg)
            if key in ["fps"]:
                self._fps = float(arg)
            if key in ["easingFunction", "easing_function", "easeFun", "ease_fun"] and isinstance(arg, Ease):
                self._easeFun = arg
    
            self._animCounter = 0.0
            self._easeVals = np.array(())
            self._easeDeltas = np.array(())
            
        if len(self._targetObjects) == 0:
            raise Exception("must pass at least one from/start/obj value")

    def begin(self):
        """ the initial object is animated and the target object moved
            to be where it will be after the animation and hidden.\n
            Once the animation has finished, the initial object is deallocated
            and the target object is made visible, i.e. un-hidden
        """

        # for self-animation (e.g. fading, translating, rotating, scaling)
        # NB: for cross-animation (e.g. transforming) this should be pre-set
        if len(self._animatedObjects) == 0:
            # make copies that will be animated
            self._animatedObjects = [o.copy() for o in self._targetObjects]
        
        # calculate all easing deltas for each iteration of the animation
        newEaseVals = []
        for i in range(self._animationLength()):
            newEaseVals.append(self._easeFun(i/(self._animationLength()))) # FIXME: the -1 issue for frame counting
        self._easeVals = np.array(newEaseVals)
        self._easeDeltas = np.diff(np.array(newEaseVals))
        self._easeDeltas = np.concatenate((np.array((0.0,)), self._easeDeltas))

        # reset the animation (iteration) counter
        self._animCounter = 0

        # hide all targets
        [o.hide() for o in self._targetObjects]

        return self._animationLength() + 1

    def getAnimatedObjects(self):
        return self._animatedObjects

    def getTargetObjects(self):
        return self._targetObjects

    def next(self) -> bool:
        """
        Returns whether another animation iteration follows.\n
        Inhereting class must override (and not call) this method.
        """
        raise Exception("{} must override Animation.next()".format(self.__class__.__name__))

    def finish(self) :
        """ Returns all redundant (i.e. animated) objects """
        # hides all animated objects
        [o.hide() for o in self._animatedObjects]
        # show all targets
        [o.show() for o in self._targetObjects]

    def _animationLength(self):
        """ Returns the number of iterations required for this animation """
        # -1 because last frame is finished animation
        iterations = round(self._fps * self._animTime) - 1
        return self._fps if iterations <= 0 else iterations        

class AnimationOut(Animation):

    def begin(self):
        ret = super().begin()
        self._easeVals = np.flip(self._easeVals)
        self._easeDeltas = np.flip(self._easeDeltas)
        return ret
