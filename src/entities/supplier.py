import logging
from time import sleep

import zmq

logger = logging.getLogger()


class Supplier:
    _storefront_socket: zmq.Socket

    def __init__(self, storefront_port: int):
        context = zmq.Context.instance()
        self._storefront_socket = context.socket(zmq.REP)
        self._storefront_socket.bind(f"tcp://*:{storefront_port}")

    def run(self):
        while True:
            quantity_requested = int(self._storefront_socket.recv_string())

            self._storefront_socket.send_string(str(quantity_requested))

            logger.info(f"{quantity_requested} parts sent.")
