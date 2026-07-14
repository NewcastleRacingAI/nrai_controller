import math

def adaptive_scale(congruence: float, minimum: float = 3.5, maximum: float = 10.0, exp: float = 2):
    congruence = -(((1*congruence)-1)**(exp))+1 # Maps linear [0, 1] of "congruence" variable to polynomial for steeper growth and earlier peaking.
    speed = minimum + (congruence * (maximum - minimum))
    return speed
