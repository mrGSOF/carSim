import math

def MxV_2x2(M,V) -> list:
    """ Return the result of 2x2 matrix and 2D vector multiplication """
    O = [0,0]
    O[0] = M[0][0]*V[0] +(M[0][1]*V[1])
    O[1] = M[1][0]*V[0] +(M[1][1]*V[1])    
    return O

def addV_2D(V1, V2) -> list:
    """ Return the result of 2D vector addition """
    return [V1[0]+V2[0], V1[1]+V2[1]]

def absV_2D(V) -> float:
    """ Return the magnitude of 2D vector """
    return math.sqrt((V[0]**2) +(V[1]**2))

def MxV(M,V) -> list:
    """ Return the result of NxM matrix and M vector multiplication """
    N = len(M)
    O = [0]*N
    for r,row in enumerate(M):
        for m,v in zip(row,V):
            O[r] += m*v
    return O
    
def addV(V1, V2) -> list:
    """ Return the result of vector addition """
    O = [0]*len(V1)
    i = 0
    for v1,v2 in zip(V1, V2):
        O[i] = v1+v2
        i += 1
    return O

def absV(V) -> float:
    """ Return the magnitude of vector """
    s2 = 0
    for v in V:
        s2 += v**2
    return math.sqrt(s2)

def angleV(V) -> float:
    """ Return the angle of 2D vector """
    return math.atan2(V[1], V[0])

def polarV(V) -> float:
    """ Return the polar coordinates of 2D vector """
    return [absV(V), angleV(V)]
    
def genR(a) -> list:
    """ Return the 2D rotation matrix """
    cosA = math.cos(a)
    sinA = math.sin(a)
    return [[cosA,-sinA],[sinA,cosA]]

def negR(R) -> list:
    R[0][1] *= -1
    R[1][0] *= -1
    return R

def radToDeg(rad) -> float:
    """Convert radians to degrees"""
    return 180*rad/math.pi # or use this math.degrees(rad)

def modulu(val, modulu):
    while val > modulu:
        val -= modulu
    while val < -modulu:
        val += modulu
    return val
    
def clip(val, Min, Max) -> float:
    """ Return the cliped (clamp) result of the input value """
    if val < Min:
        val = Min
    elif val > Max:
        val = Max
    return val
