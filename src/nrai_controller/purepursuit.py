import math
from dataclasses import dataclass


@dataclass(slots=True)
class AckermannDrive:
    steering_angle: float = 0.0
    steering_angle_velocity: float = 1.0
    speed: float = 0.5
    acceleration: float = 0.25
    jerk: float = 0.1


def get_angle(path: object) -> AckermannDrive:
    lookahead_distance = 2
    wheel_base = 1.53

    path.insert(0, (float(0), float(0)))
    for i in range(0, len(path) - 1):
        gradient = float(999)
        if (path[i][0] - path[i + 1][0]) != 0:
            gradient = (path[i][1] - path[i + 1][1]) / (path[i][0] - path[i + 1][0])
        constant = path[i][1] - (gradient * path[i][0])

        a = 1 + math.pow(gradient, 2)
        b = 2 * gradient * constant
        c = math.pow(constant, 2) - math.pow(lookahead_distance, 2)

        discriminant = math.pow(b, 2) - (4 * a * c)

        if discriminant >= 0:
            xplus = ((-1 * b) + math.sqrt(discriminant)) / (2 * a)
            xminus = ((-1 * b) - math.sqrt(discriminant)) / (2 * a)

            yplus = (gradient * xplus) + constant
            yminus = (gradient * xminus) + constant

            if xplus == 0:
                xplus = float(0.00001)
            if xminus == 0:
                xminus = float(0.00001)

            if (
                min(path[i + 1][0], path[i][0])
                <= xplus
                <= max(path[i + 1][0], path[i][0])
            ):
                a = (math.atan(yplus / xplus) % math.pi) - math.pi / 2
                angle = math.atan(2 * wheel_base * math.sin(a) / (lookahead_distance))
                return AckermannDrive(steering_angle=angle)
            elif (
                min(path[i + 1][0], path[i][0])
                <= xminus
                <= max(path[i + 1][0], path[i][0])
            ):
                a = (math.atan(yminus / xminus) % math.pi) - math.pi / 2
                angle = math.atan(2 * wheel_base * math.sin(a) / (lookahead_distance))
                return AckermannDrive(steering_angle=angle)
    return AckermannDrive()
