#!/usr/bin/env python3
import struct
import argparse
from multiprocessing import Queue
from .purepursuit import get_angle
from .adaptive_scale import adaptive_scale
import logging
from time import sleep

import socket

socket_path = "/run/nims/lower_ctrl.sock"
logger = logging.getLogger()

def connect_socket():
    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            s.connect(socket_path)
            s.sendall(struct.pack("<BI", 0x07, 0x01))
            logger.info("Connected to NIMS")

            # Initialise values
            send_packet(0x01, 0.0, s)  # Steering angle           (dead ahead)
            send_packet(0x02, 1.0, s)  # Steering angle velocity  (our previous default)
            send_packet(0x03, 10.0, s) # Speed                    (our previous default)
            send_packet(0x04, 5.0, s)  # Acceleration             (our previous default)
            send_packet(0x05, 0.1, s)  # Jerk                     (our previous default)
            send_packet(0x00, 0, s)    # Report
            
            return s
        except:
            logger.error("Could not connect to NIMS, retrying in 1 second...")
            sleep(1)

def send_packet(msg_id, data, sock):
    # Set packet
    packet = bytes()
    if msg_id in range(0, 6):
        packet = struct.pack("<Bf", msg_id, data)
    elif msg_id==8:
        packet = struct.pack("<BI", msg_id, data)
    
    # Attempt transmission
    try:
        sock.sendall(packet)
        logging.debug("Sent %s", packet)
        return True
    except:
        return False


def main(args: argparse.Namespace):
    topics: dict[str, Queue] = args.topics or {}
    logging.basicConfig(format=args.logger_format or "", level=args.actual_verbosity() if args.actual_verbosity else logging.INFO)
    logger = logging.getLogger()
    logger.info("Initializing...")

    # --- Set up Code ---
    if args.control_topic not in topics:
        raise ValueError(f"No '{args.control_topic}' topic to listen to.")

    control_queue = topics[args.control_topic]

    msg_types = {
        "report": 0x00,
        "steering_angle": 0x01,
        "steering_angle_velocity": 0x02,
        "speed": 0x03,
        "acceleration": 0x04,
        "jerk": 0x05,
    }

    s = connect_socket()
    active_attributes = ["steering_angle", "speed"]

    euclidean_distance = lambda line: ((line[0][0] - line[1][0])**2 + (line[0][1] - line[1][1])**2)**(0.5)

    while True:
        logger.debug("Starting loop")
        while control_queue.qsize() > 1:
            logger.debug("Emptying queue")
            control_queue.get()
        path = control_queue.get()
        logger.debug("Received %s", path)

        congruence: float
        for i in range(len(path)-1):
            congruence += euclidean_distance([path[i], path[i+1]])
        congruence = euclidean_distance([path[0], path[-1]]) / congruence # Should be in [1, 0] as direct is always <= |path|

        drive = get_angle(path)
        drive.speed = adaptive_scale(drive, congruence)

        succesfully_sent = True
        for attribute in active_attributes:
            msg_id = msg_types[attribute]
            data = getattr(drive, attribute)
            succesfully_sent &= send_packet(msg_id, data, s)
        succesfully_sent &= send_packet(msg_types["report"], 0x00000000, s)

        if not succesfully_sent:
            s = connect_socket()

if __name__ == "__main__":
    main()
