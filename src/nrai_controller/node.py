#!/usr/bin/env python3
import struct
import os
import argparse
from multiprocessing import Queue
from .purepursuit import get_angle
import logging

fifo_out = "/tmp/lower_ctrl_cmd"

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

    while True:
        path = control_queue.get()
        drive = get_angle(path)

        new_instruction = struct.pack(
            "<5fI",
            drive.steering_angle,
            drive.steering_angle_velocity,
            drive.speed,
            drive.acceleration,
            drive.jerk,
            0xFFFFFFFF,
        )

        logger.info("Path: %s => Control %s", path, new_instruction)
        try:
            fd = os.open(fifo_out, os.O_WRONLY)
            with open(fd, "wb") as fifo:
                fifo.write(new_instruction)
        except FileNotFoundError:
            print(
                f"NRAI_CONTROLLER: Could not access FIFO {fifo_out}. Likely not yet configured."
            )
        except BrokenPipeError:
            print(f"NRAI_CONTROLLER: FIFO {fifo_out} terminated.")


if __name__ == "__main__":
    main()
