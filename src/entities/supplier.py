import logging
from time import sleep

import zmq

from src.constants import SUPPLIER_PER_ITEM_SENT_DELAY

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

            logger.info(f"{quantity_requested} parts requested.")

            sleep(SUPPLIER_PER_ITEM_SENT_DELAY * quantity_requested)
            self._storefront_socket.send_string(str(quantity_requested))

            logger.info(f"{quantity_requested} parts sent.")
