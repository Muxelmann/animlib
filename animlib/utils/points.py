import numpy as np

def convertToPoints(val) -> np.ndarray:
    """
    Converts `val` (`str` or `NP.NDARRAY`) into `N x 2` array
    """
    if isinstance(val, str):
        val = val.replace(",", "")
        val = np.array([float(v) for v in val.split(" ") if v != ""])
    elif isinstance(val, (list, tuple)):
        val = np.array([float(v) for v in val])
    if isinstance(val, np.ndarray) and np.size(val) % 2 == 0:
        return val.reshape((-1, 2))
    return None


def interpolateLinear(start, end, num=4):
    x = np.linspace(start[0,0], end[0,0], num).reshape((num, 1))
    y = np.linspace(start[0,1], end[0,1], num).reshape((num, 1))
    return np.concatenate((x, y), 1)

def sliceBezier(points, t=0.5):
    if not isinstance(points, np.ndarray) or np.size(points, 0) != 4 or np.size(points, 1) != 2:
        raise Exception("4x2 ndarray and 0<=t<=1 must be passed")
    
    x1, y1 = points[0, 0], points[0, 1]
    x2, y2 = points[1, 0], points[1, 1]
    x3, y3 = points[2, 0], points[2, 1]
    x4, y4 = points[3, 0], points[3, 1]

    x12 = (x2-x1)*t+x1
    y12 = (y2-y1)*t+y1

    x23 = (x3-x2)*t+x2
    y23 = (y3-y2)*t+y2

    x34 = (x4-x3)*t+x3
    y34 = (y4-y3)*t+y3

    x123 = (x23-x12)*t+x12
    y123 = (y23-y12)*t+y12

    x234 = (x34-x23)*t+x23
    y234 = (y34-y23)*t+y23

    x1234 = (x234-x123)*t+x123
    y1234 = (y234-y123)*t+y123

    return np.array([(x1, y1),
        (x12, y12), (x123, y123), (x1234, y1234),
        (x234, y234), (x34, y34), (x4, y4)]).reshape((7, 2))
