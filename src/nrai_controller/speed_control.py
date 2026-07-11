"""Speed control for shen_controller.

Pure Pursuit (get_angle) sets the AckermannDrive's steering_angle. This fills
in drive.speed: ease off when steering hard, run up to v_max on the straights.
It replaces the hardcoded `drive.speed = 0.5` in the controller.

Method (grip limit):
    R     = wheel_base / tan(|steering_angle|)   # turn radius the car will follow
    v     = sqrt(mu * g * R)                     # fastest speed within tyre grip
    speed = clip(v, v_min, v_max)

Straight (steering ~ 0) -> R huge -> clamped to v_max.

Works whether AckermannDrive is the ROS message (main branch) or a plain Python
object (fullstack branch): it only reads .steering_angle and writes .speed.
"""

import math

G = 9.81           # m/s^2
WHEEL_BASE = 1.53  # m, matches wheel_base in purepursuit.py


def set_drive_speed(drive, mu=1.0, v_max=10.0, v_min=0.5, wheel_base=WHEEL_BASE):
    """Set drive.speed (m/s) from drive.steering_angle, in place. Returns drive.

    ---- PLACEHOLDERS: confirm with the team / measure on the car ----
    mu     : tyre-track friction coefficient
    v_max  : top-speed cap (m/s)
    v_min  : floor speed while driving (m/s)
    """
    delta = abs(float(drive.steering_angle))

    if delta < 1e-4:                       # essentially straight -> top speed
        drive.speed = float(v_max)
        return drive

    radius = wheel_base / math.tan(delta)  # turn radius (m)
    v = math.sqrt(mu * G * radius)         # grip-limited speed
    drive.speed = float(min(max(v, v_min), v_max))
    return drive
