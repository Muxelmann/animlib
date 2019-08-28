import os, re
from xml.dom import minidom
import numpy as np

from animlib.geometies.base import Base, Center
from animlib.utils.points import convertToPoints, interpolateLinear

class SVG(Base):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._svgFile = None

        for key in kwargs:
            arg = kwargs[key]
            if key in ["svg", "SVG", "svgFile", "svg_file"]:
                self._svgFile = arg

        if self._svgFile is None or not isinstance(self._svgFile, str) or self._svgFile.split(".")[-1].lower() != "svg":
            return

        if os.path.exists(self._svgFile):
            self._extractSvg()

        # move to coordinate (0, 0) by default
        self.translateBy(-self.getCenter())

        for key in kwargs:
            arg = kwargs[key]
            if key in ["x", "X"]:
                self.translateBy(convertToPoints((arg, 0)))
            if key in ["y", "Y"]:
                self.translateBy(convertToPoints((0, arg)))

    def _extractSvg(self):
        doc = minidom.parse(self._svgFile)
        self._pathsUsed = {}
        for svg in doc.getElementsByTagName("svg"):
            self._extractBaseObjectsFrom(svg)
        doc.unlink()

        # self.translateBy((-300, -300))
        self._applyUses()
        # print([i for i in zip(self._pathIDs, self._paths)])

    def _extractBaseObjectsFrom(self, element):
        # assure a minidom element is being converted
        if not isinstance(element, minidom.Element):
            return

        if element.tagName in ["defs", "g", "svg"]:
            for c in element.childNodes:
                self._extractBaseObjectsFrom(c)
        elif element.tagName == "style":
            print("implement stype")
        elif element.tagName == "path":
            self._newPathObj(element)
        elif element.tagName == "use":
            self._newUseObj(element)
        elif element.tagName == "rect":
            self._newRectObj(element)
        elif element.tagName == "circle":
            print("implement circle")
        elif element.tagName == "ellipse":
            print("implement ellipse")
        elif element.tagName in ["polygon", "polyline"]:
            print("implement polygon/-line")
        else:
            print("unknown SVG object: {}".format(element.tagName))

    def _getPathCommands(self):
        result = [
            "M",  # moveto
            "L",  # lineto
            "H",  # horizontal lineto
            "V",  # vertical lineto
            "C",  # curveto
            "S",  # smooth curveto
            "Q",  # quadratic Bezier curve
            "T",  # smooth quadratic Bezier curveto
            "A",  # elliptical arc
            "Z",  # closepath
        ]
        result += [s.lower() for s in result]
        return result

    def addPath(self, pathID):
        """ To enable translation of SVG path, store IDs for each (sub-)path """
        super().addPath()
        # Path ID: SVG-ID # SUB-PATH_COUNTER
        
        pathID += "#0"
        i = 1
        while pathID in self._pathsUsed.keys():
            pathID = "#".join(pathID.split("#")[:-1]) + "#{}".format(i)
            i += 1
        self._pathsUsed[pathID] = []

    def _newPathObj(self, element):
        """ Converts minidom element that is SVG path into points for _paths """
        if not isinstance(element, minidom.Element):
            return

        pathID = element.getAttribute("id")
        pathString = element.getAttribute("d")

        pattern = "[{}]".format("".join(self._getPathCommands()))
        pairs = list(zip(
            re.findall(pattern, pathString),
            re.split(pattern, pathString)[1:]
        ))

        prevCommand = None
        for command, coordString in pairs:
            isLower = command.islower()
            if isLower:
                print("LOWER! -> Fix relative coordinates")
            command = command.upper()

            newPoint = convertToPoints(coordString)
            if command == "M": # moveto
                self.addPath(pathID)
            elif command in ["L", "H", "V"]:
                if command == "H": # horizontal line to
                    newPoint = self.getNthPoint(-1)
                    newPoint[0, 0] = float(coordString)
                elif command == "V": # vertical line to
                    newPoint = self.getNthPoint(-1)
                    newPoint[0, 1] = float(coordString)
                newPoint = interpolateLinear(self.getNthPoint(-1), newPoint)[1:,:]
            elif command == "C": # C x1 y1, x2 y2, x y
                pass
            elif command == "S": # S x2 y2, x y
                if prevCommand in ["C", "S"]: # otherwise treat as C
                    lP1 = self.getNthPoint(-1)
                    lP2 = self.getNthPoint(-2)
                    newPoint = np.concatenate((2*lP1-lP2, newPoint), 0)
            elif command == "Q": # Q x1 y1, x y
                newPoint = np.concatenate((newPoint[0, :].reshape((1, 2)), newPoint), 0)
            elif command == "T": # T x y
                if prevCommand in ["Q", "T"]: # otherwise treat as Q
                    lP1 = self.getNthPoint(-1)
                    lP2 = self.getNthPoint(-2)
                    newPoint = np.concatenate((lP2-lP1+lP2, newPoint), 0)
                newPoint = np.concatenate((newPoint[0, :].reshape((1, 2)), newPoint), 0)
            elif command == "A": # elliptical arc
                print("A missing")
            elif command == "Z": # closepath
                pass
            self.addPoint(newPoint)
            prevCommand = command
            
    def _newUseObj(self, element):
        if not isinstance(element, minidom.Element):
            return

        pathID = element.getAttribute("xlink:href")[1:]
        dx = element.getAttribute("x") if element.hasAttribute("x") else 0.0
        dy = element.getAttribute("y") if element.hasAttribute("y") else 0.0

        # check if path has been used already
        mathPathKeys = [k for k in self._pathsUsed.keys() if "#".join(k.split("#")[:-1]) == pathID]
        for key in mathPathKeys:
            self._pathsUsed[key].append((dx, dy))
        # print([(k, self._pathsUsed[k]) for k in self._pathsUsed.keys()])

    def _newRectObj(self, element):
        if not isinstance(element, minidom.Element):
            return
        x = float(element.getAttribute("x")) if element.hasAttribute("x") else 0.0
        y = float(element.getAttribute("y")) if element.hasAttribute("y") else 0.0
        w = float(element.getAttribute("width")) if element.hasAttribute("width") else 0.0
        h = float(element.getAttribute("height")) if element.hasAttribute("height") else 0.0

        super().addPath()
        start = convertToPoints((x, y))
        self.addPoint(start)
        end = convertToPoints((x+w, y))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((x+w, y+h))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((x, y+h))
        self.addPoint(interpolateLinear(start, end)[1:,:])
        start = end
        end = convertToPoints((x, y))
        self.addPoint(interpolateLinear(start, end)[1:,:])

    def _applyUses(self):
        definitions = len(self._pathsUsed)
        for i, key in zip(range(definitions), self._pathsUsed.keys()):
            for offset in self._pathsUsed[key]:
                super().addPath()
                self.addPoint(self._paths[i])
                self.translateBy(offset, -1)

        for _ in range(len(self._pathsUsed)):
            self.clearPath(0)