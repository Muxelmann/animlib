#!/usr/bin/env python
from animlib import *

def main():
    print("Started animlib")

    c = Canvas("test")

    s1 = Latex(expression="ax^2+bx+c")
    s2 = Latex(expression="x_{1,2}=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}")

    # s = SVG(svg="test.svg")
    s1.scaleBy(10)
    s2.scaleBy(10)
    s1.translateBy(-s1.getCenter())
    s2.translateBy(-s2.getCenter())

    # o = s1.getOutline()
    # d = np.sum(np.abs(s1.getOutline()),0)
    # r = Rect(x=o[0,0], y=o[0,1], w=d[0], h=d[1], fillColor=ColorMap.BLUE_E, strokeColor=ColorMap.BLUE_A, strokeWidth=10)
    # r.scaleBy(1.2)

    # circ = Circle(r=500, fillColor=ColorMap.GREEN_E, strokeColor=ColorMap.BLUE_E, strokeWidth=25)

    # l1 = Line((-200, 0), (200, 0), strokeWidth=5)
    # l2 = Line((250, -30), (-100, 148), strokeWidth=5)

    # c.addGeometry(s2)
    # c.addGeometry(r)
    # c.addGeometry(l1)
    # c.saveToPNG()
    c.animate(Unveil(s1))
    c.wait(0.1)
    c.animate(Transform(start=s1, end=s2))
    # c.animate(Transform(start=circ, end=l2))
    # c.addGeometry(s1)

    # c.wait(0.5)
    # c.animate(
    #     Unveil(r, circ),
    #     FadeIn(s1),
    #     )
    # c.wait(0.5)
    # c.animate(FadeOut(circ))
    # c.wait(0.5)
    # c.animate(Hide(r))
    # c.wait(1)


if __name__ == "__main__":
    main()
