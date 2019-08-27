#!/usr/bin/env python
from animlib import *

def main():
    print("Started animlib")

    c = Canvas("test")

    s1 = Latex(expression="ax^2+bx+c")
    s2 = Latex(expression="x_{1,2}=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}")

    s1.scaleBy(10)
    s2.scaleBy(10)
    s1.translateBy(-s1.getCenter())
    s2.translateBy(-s2.getCenter())

    
    c.addGeometry(s1)
    c.saveToPNG()

    c.animate(Unveil(s1))
    c.wait(0.1)
    c.animate(Transform(start=s1, end=s2))
    

if __name__ == "__main__":
    main()
