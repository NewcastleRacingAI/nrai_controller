#!/usr/bin/env python3
import struct
import os
import argparse
from multiprocessing import Queue
from .purepursuit import get_angle
import logging

from enum import Enum

import socket

socket_path = "/run/nims/lower_ctrl.sock"

def send_packet(msg_id, data, sock):
    packet = struct.pack(
        "<Bf",
        msg_id,
        data,
    )
    sock.sendall(packet)

def main(args: argparse.Namespace):
    topics: dict[str, Queue] = args.topics or {}
    logging.basicConfig(
        format=args.logger_format or "", level=args.verbosity or logging.INFO
    )
    logger = logging.getLogger()

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
        "finished": 0x06
    }

    s = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    s.connect(socket_path)

    while True:
        while control_queue.qsize()>1:
            control_queue.get()
        path = control_queue.get()
        drive = get_angle(path)

        #new_instruction = struct.pack(
        #    "<5fI",
        #    drive.steering_angle,
        #    drive.steering_angle_velocity,
        #    drive.speed,
        #    drive.acceleration,
        #    drive.jerk,
        #    0xFFFFFFFF,
        #)

        #logger.info("Path: %s => Control %s", path, new_instruction)
        for attribute in list(drive.__dict__).keys():
            msg_id = msg_types[attribute]
            data = getattr(drive, attribute)
            send_packet(msg_id, data, s)
        send_packet(msg_types["report"], 0x00000000, s)

if __name__ == "__main__":
    main()
