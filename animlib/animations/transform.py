from animlib.animations.animation import Animation

class Transform(Animation):

    def begin(self) -> int:
        ret = super().begin()

        self._animatedPointDifferences = []
        self._animatedFillColorDifferences = []
        self._animatedStrokeColorDifferences = []
        self._animatedStrokeWidthDifferences = []


        if len(self._animatedObjects) > 1:
            raise Exception("can only animate a single object")

        if len(self._animatedObjects) != len(self._targetObjects):
            raise Exception("can only animate matching number of objects")
        
        
        for a, t in zip(self._animatedObjects, self._targetObjects):
            if not a.pathsMatch(t):
                while a.getNumPaths() < t.getNumPaths():
                    a.duplicatePath()
                while a.getNumPaths() > t.getNumPaths():
                    t.duplicatePath()
                
            pointsOfPathsMatch = a.pointsOfPathsMatch(t)
            if not all(pointsOfPathsMatch):

                for p in range(a.getNumPaths()): # == t.getNumPaths()
                    while a.getNumPointsPerPath(p) < t.getNumPointsPerPath(p):
                        a.interpolatePath(p)
                    while a.getNumPointsPerPath(p) > t.getNumPointsPerPath(p):
                        t.interpolatePath(p)

            self._animatedPointDifferences += [t.getPoints() - a.getPoints()]
            self._animatedFillColorDifferences += [t.getFillColor() - a.getFillColor()]
            self._animatedStrokeColorDifferences += [t.getStrokeColor() - a.getStrokeColor()]
            self._animatedStrokeWidthDifferences += [t.getStrokeWidth() - a.getStrokeWidth()]
        
        return ret

    def next(self) -> bool:
        if self._animCounter > self._animationLength():
            return False
        # if end is reached, clean up and return false
        if self._animCounter == self._animationLength():
            self.finish()
        else:
            # animate
            for i in range(len(self._animatedObjects)):
                # print(self._animatedObjects[0]._fillColor)
                # print(self._targetObjects[i].getFillColor() +
                #     self._animatedFillColorDifferences[i] * self._easeVals[self._animCounter])
                self._animatedObjects[i].translateBy(
                    self._animatedPointDifferences[i] * self._easeDeltas[self._animCounter])
                self._animatedObjects[i].setFill(
                    self._animatedObjects[i].getFillColor() +
                    self._animatedFillColorDifferences[i] * self._easeDeltas[self._animCounter])
                self._animatedObjects[i].setStroke(
                    color=
                        self._animatedObjects[i].getStrokeColor() +
                        self._animatedStrokeColorDifferences[i] * self._easeDeltas[self._animCounter],
                    width=
                        self._animatedObjects[i].getStrokeWidth() +
                        self._animatedStrokeWidthDifferences[i] * self._easeDeltas[self._animCounter])
        self._animCounter += 1
        return True

    def _directPointDifference(self, ele1, ele2):
        return ele2.getPoints() - ele1.getPoints()