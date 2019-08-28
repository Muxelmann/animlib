import numpy as np
try:
    import cairo
except:
    import cairocffi as cairo
from enum import Enum
import copy

from animlib.utils.points import convertToPoints, sliceBezier
from animlib.utils.colors import convertToColor, ColorComponent

class Center(Enum):
    BY_POINTS = 0
    BY_OUTLINE = 1

class Base():
    """
    Defines the basic geometry using points, stroke and fill information
    """

    def __init__(self, *args, **kwargs):
        assert len(args)==0, "for Base objects, each argument must be named"

        self.clearPoints()
        self._paths = []
        self._fillGradient = None
        self._fillColor = np.array((1.0, 1.0, 1.0, 1.0))
        self._strokeGradient = None
        self._strokeColor = np.array((1.0, 1.0, 1.0, 1.0))
        self._strokeWidth = 0.10
        self._isHidden = False

        for key in kwargs:
            arg = kwargs[key]
            if key in ["points", "pts"]:
                self.addPoint(convertToPoints(arg))
            elif key in ["fillColor", "fill_color"]:
                self.setFill(color=arg)
            elif key in ["strokeColor", "stroke_color"]:
                self.setStroke(color=arg)
            elif key in ["strokeWidth", "stroke_width"]:
                self.setStroke(width=arg)
            elif key in ["hidden", "isHidden", "is_hidden"]:
                self._isHidden = arg
            
    def __repr__(self):
        return "{}[{}]: 0x{:x}".format(
            self.__class__.__name__,
            "H" if self._isHidden else "V",
            id(self))
    
    def copy(self):
        """ Returns a copy (i.e. deep copy) of the object """
        return copy.deepcopy(self)

    def hide(self, isHidden=True):
        """ Hides the geometry from being drawn """
        self._isHidden = isHidden if isinstance(isHidden, bool) else True

    def show(self, isShown=True):
        """ Shows the geometry when being drawn """
        self._isHidden = not isShown if isinstance(isShown, bool) else False

    def addPoint(self, point):
        """ Adds one ore more points """
        if isinstance(point, (list, tuple)):
            [self.addPoint(p) for p in point]
        elif isinstance(point, str):
            point = convertToPoints(point)
        elif not isinstance(point, np.ndarray) and np.size(point, 1) != 2:
            return
        assert len(self._paths) > 0, "Object has no path"
        self._paths[-1] = np.concatenate((self._paths[-1], point), 0)

    def duplicatePath(self, idx=None):
        if not isinstance(idx, int):
            idx = np.random.randint(len(self._paths))   
        self._paths.insert(idx, np.array(self._paths[idx]))

    def pathsMatch(self, target):
        if not isinstance(target, Base):
            raise Exception("can only compare a target of type Base")
        return self.getNumPaths() == target.getNumPaths()

    def pointsOfPathsMatch(self, target):
        if not self.pathsMatch(target):
            raise Exception("number of paths of target must match Base")
        r = [] # result
        for p1, p2 in zip(self._paths, target._paths):
            r += [np.size(p1, 0) == np.size(p2, 0)]
        return r

    def interpolatePath(self, p):
        """ Interpolates the points at path p by an additional 3 bezier anchors """
        path = self._paths[p]
        at = np.random.randint(int((np.size(path, 0)-1)/3)) * 3 + 1
        points = path[at-1:at+3, :]

        self._paths[p] = np.concatenate((
            path[:at-1, :],
            sliceBezier(points),
            path[at+3:, :]), 0)

    def getNumPoints(self) -> int:
        return int(np.size(self.getPoints(), 0))

    def getNumPointsPerPath(self, p) -> int:
        return np.size(self._paths[p], 0)

    def getNumPaths(self) -> int:
        return len(self._paths)

    def getNthPoint(self, n) -> np.ndarray:
        """ Returns the Nth point """
        allPoints = self.getPoints()
        if not isinstance(n, int):
            raise Exception("n must be an integer")
        if np.size(allPoints, 0) == 0:
            return None
        return allPoints[n, :].reshape((1, 2))

    # def getFirstPoint(self) -> np.ndarray:
    #     """ Returns the first added point """
    #     if np.size(self.getPoints(), 0) == 0:
    #         return None
    #     return self.getPoints()[0, :].reshape((1, 2))

    # def getLastPoint(self) -> np.ndarray:
    #     """ Returns the last added point """
    #     if np.size(self.getPoints(), 0) == 0:
    #         return None
    #     return self.getPoints()[-1, :].reshape((1, 2))

    # def getSecondLastPoint(self) -> np.ndarray:
    #     """ Returns the second to last point added """
    #     if np.size(self.getPoints(), 0) < 2:
    #         return None
    #     return self.getPoints()[-2, :].reshape((1, 2))

    def getPoints(self) -> np.ndarray:
        """ Returns all points """
        return np.concatenate(self._paths, 0)

    def setStroke(self, color=None, component=None, opacity=None, width=None, gradient=None):
        """ Sets stroke properties regarding color, opacity and width """
        # specify the color directly
        if color is not None:
            # if RGBA component is not specified ...
            if component is None:
                # ... get the 4d color vector and assign
                strokeColor = convertToColor(color) 
                if strokeColor is not None and isinstance(strokeColor, np.ndarray):
                    self._strokeColor = strokeColor

            # if RGBA component is specified and the color is correct format ...
            elif isinstance(component, ColorComponent) and isinstance(strokeColor, (int, float)): 
                # ... assign color component directly
                self._strokeColor[component.value] = float(strokeColor)

            self._strokeGradient = None

        # specify gradient
        elif gradient is not None:
            self._strokeGradient = gradient if isinstance(gradient, cairo.Gradient) else None

        # specify opacity, i.e. alpha value
        elif opacity is not None and isinstance(opacity, (float, int)):
            self._strokeColor[3] = float(opacity)

        # specify stroke width
        if width is not None and isinstance(width, (float, int)):
            self._strokeWidth = float(width)

    def getStrokeColor(self, component=None):
        if component is None:
            return self._strokeColor
        elif isinstance(component, ColorComponent):
            return self._strokeColor[component.value]

    def getStrokeWidth(self):
        return self._strokeWidth

    def setFill(self, color=None, component=None, opacity=None, gradient=None):
        """ Sets fill properties regarding color and opacity """

        # specify the color direcrly
        if color is not None:
            # if RGBA component is not specified ...
            if component is None:
                # ... get the 4d color vector and assign
                fillColor = convertToColor(color)
                if fillColor is not None and isinstance(fillColor, np.ndarray):
                    self._fillColor = fillColor
            
            # if RGBA component is specified and color is correct format ...
            elif isinstance(component, ColorComponent) and isinstance(fillColor, (int, float)):
                # ... assign color component directly
                self._fillColor[component.value] = float(fillColor)
            
            self._fillGradient = None
        
        # specify gradient
        elif gradient is not None:
            self._fillGradient = gradient if isinstance(gradient, cairo.Gradient) else None

        # specify opacity, i.e. alpha value
        elif opacity is not None and isinstance(opacity, (float, int)):
            self._fillColor[3] = float(opacity)
        

    def getFillColor(self, component=None):
        if component is None:
            return self._fillColor
        elif isinstance(component, ColorComponent):
            return self._fillColor[component.value]

    def clearPoints(self):
        """ Deletes all points """
        # self._points = np.array(()).reshape((-1, 2))
        self._paths = []

    def clearPath(self, pathIdx=None):
        """ Equal to clearPoints when not passing a path index """
        if pathIdx is None:
            self.clearPoints()
        elif isinstance(pathIdx, int):
            del self._paths[pathIdx]

    def addPath(self):
        """ Adds a new series of points of a path """
        self._paths.append(np.array(()).reshape((-1, 2)))

    def getOutline(self, pathIdx=None):
        """ Returns the corner coordinates of the outline """
        if pathIdx is None:
            return np.concatenate((
                np.min(self.getPoints(), 0).reshape((1, 2)),
                np.max(self.getPoints(), 0).reshape((1, 2))
                ), 0)
        elif isinstance(pathIdx, int) and pathIdx < len(self._paths):
            return np.concatenate((
                np.min(self._paths[pathIdx], 0).reshape((1, 2)),
                np.max(self._paths[pathIdx], 0).reshape((1, 2)),
            ), 0)
        raise Exception("cannot get outline for pathIdx: {}".format(pathIdx))

    def getDimensions(self, pathIdx=None):
        """ Returns the width and height of the geometry or path of geometry """
        outline = self.getOutline(pathIdx)
        return np.diff(outline, 1, 0)

    def getCenter(self, center=Center.BY_OUTLINE):
        """ Returns the center coordinate """
        if np.size(self.getPoints(), 0) == 0:
            return None
        
        if isinstance(center, Center):
            if center == Center.BY_OUTLINE:
                outline = self.getOutline()
                return np.mean(outline, 0)
            else:
                return np.mean(self.getPoints(), 0)
        else:
            return convertToPoints(center)

    def rotateBy(self, angle, center=Center.BY_OUTLINE):
        """ Rotates all points in each path by an angle around a center """
        center = self.getCenter(center).dot(np.array((1, 1j))).reshape((-1, 1))
        for i in range(len(self._paths)):
            # get points and turn into complex plane
            points = self._paths[i].dot(np.array((1, 1j))).reshape((-1, 1))
            # normalize points for rotation using center
            points -= center
            # rotate points by unity vector at an angle in compelex plane
            points *= (np.cos(angle) + np.sin(angle)*1j) # FIXME change sign if y-axis is upside down 
            # shift back to original location
            points = points + center
            # convert into normal coordinates
            self._paths[i] = np.concatenate((
                np.real(points).reshape((-1, 1)),
                np.imag(points).reshape((-1, 1))), 1)

    def scaleBy(self, scale, center=Center.BY_OUTLINE):
        """ Scale the geometry by a value from center """
        center = self.getCenter(center).dot(np.array((1, 1j))).reshape((-1, 1))
        for i in range(len(self._paths)):
            # get points and turn into complex plane
            points = self._paths[i].dot(np.array((1, 1j))).reshape((-1, 1))
            # normalize points for rotation using center
            points -= center
            # rotate points by unity vector at an angle in compelex plane
            points *= scale
            # shift back to original location
            points = points + center
            # convert into normal coordinates
            self._paths[i] = np.concatenate((
                np.real(points).reshape((-1, 1)),
                np.imag(points).reshape((-1, 1))), 1)

    def translateBy(self, translation, pathIdx=None):
        """ Translates the points of a paz by a vector described by `translation` """
        # make sure translation is a vector
        translation = convertToPoints(translation)
        if not isinstance(translation, np.ndarray):
            raise Exception("cannot translate unless a valid vector is provided")

        if isinstance(pathIdx, int):
            self._paths[pathIdx] += translation
        if np.size(translation, 0) == 1:
            # translate uniformly
            for i in range(self.getNumPaths()):
                # translate points
                self._paths[i] += translation
        elif np.size(translation, 0) == np.size(self.getPoints(), 0):
            # translate points of paths individually
            startIdx = 0
            for i in range(self.getNumPaths()):
                endIdx = startIdx + np.size(self._paths[i], 0)
                self._paths[i] += translation[startIdx:endIdx,:]
                startIdx = endIdx

    def draw(self, context):
        """ Draws on the geometry on `context` (i.e. cairo) """        
        if len(self._paths) == 0 or not isinstance(context, cairo.Context):
            return
        
        # don't draw is hidden
        if self._isHidden:
            return
        
        for points in self._paths:
            context.move_to(points[0, 0], points[0, 1])
            # for i in range(1, np.size(points, 0)):
            #     context.line_to(points[i, 0], points[i, 1])
            for i in range(1, np.size(points, 0), 3):
                context.curve_to(
                    points[i, 0], points[i, 1],
                    points[i+1, 0], points[i+1, 1],
                    points[i+2, 0], points[i+2, 1])
            # context.close_path()

        if isinstance(self._strokeGradient, cairo.Gradient):
            context.set_source(self._strokeGradient)
        else:
            context.set_source_rgba(
                self._strokeColor[0],
                self._strokeColor[1],
                self._strokeColor[2],
                self._strokeColor[3])
        context.set_line_width(self._strokeWidth)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.stroke_preserve()

        if isinstance(self._fillGradient, cairo.Gradient):
            context.set_source(self._fillGradient)
        else:
            context.set_source_rgba(
                self._fillColor[0],
                self._fillColor[1],
                self._fillColor[2],
                self._fillColor[3])
        context.fill()
