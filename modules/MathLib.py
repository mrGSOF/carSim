import math

def MxV(M,V) -> list:
    """ Return the result of 2x2 matrix and 2D vector multiplication """
    O = [0,0]
    O[0] = M[0][0]*V[0] +(M[0][1]*V[1])
    O[1] = M[1][0]*V[0] +(M[1][1]*V[1])    
    return O

def addV(V1, V2) -> list:
    """ Return the result of 2D vector addition """
    return [V1[0]+V2[0], V1[1]+V2[1]]

def absV(V) -> float:
    """ Return the magnitude of 2D vector """
    return math.sqrt((V[0]**2) +(V[1]**2))

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
    
def clip(val, Min, Max) -> float:
    """ Return the cliped (clamp) result of the input value """
    if val < Min:
        val = Min
    elif val > Max:
        val = Max
    return val
