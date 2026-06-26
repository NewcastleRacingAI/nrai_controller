#!/usr/bin/env python3
import struct
import os
import math
import time
import pickle

from purepursuit import get_angle

fifo_in = '/tmp/PATHPLANNING_Path'
fifo_out = '/tmp/lower_ctrl_cmd'

class AckermannDrive():
    
    def __init__(self):
        self.steering_angle = float(0)
        self.steering_angle_velocity = float(1)
        self.speed = float(0.5)
        self.acceleration = float(0.25)
        self.jerk = float(0.1)

def main(args=None):
    
    while True:
        try:
            fd_in = os.open(fifo_in, os.O_RDONLY)
            with open(fd_in, "rb") as file:
                print(f"NRAI_CONTROLLER: Successfully opened {fifo_in}.")
                while True:
                    path = pickle.load(file)
                    drive = AckermannDrive()
                    
                    get_angle(path, drive)
                    steering_angle_velocity = float(1)
                    speed = float(0.5)
                    acceleration = float(0.25)
                    jerk = float(0.1)
                    
                    new_instruction = struct.pack('<5fI', drive.steering_angle, drive.steering_angle_velocity, drive.speed, drive.acceleration, drive.jerk, 0xFFFFFFFF)
                    try:
                        fd = os.open(fifo_out, os.O_WRONLY)
                        with open(fd, "wb") as fifo:
                            fifo.write(new_instruction)
                    except FileNotFoundError:
                        print(f"NRAI_CONTROLLER: Could not access FIFO {fifo_out}. Likely not yet configured.")
                    except BrokenPipeError:
                        print(f"NRAI_CONTROLLER: FIFO {fifo_out} terminated.")
        except FileNotFoundError:
            print(f"NRAI_CONTROLLER: Could not access FIFO {fifo_in}. Likely not yet configured.")
            time.sleep(0.5)
        except BrokenPipeError:
            print(f"NRAI_CONTROLLER: FIFO {fifo_in} terminated.")
        except EOFError:
            print(f"NRAI_CONTROLLER: Erroneous read of {fifo_in}")

if __name__ == '__main__':
    main()
