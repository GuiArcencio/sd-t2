from __future__ import annotations

import random
from dataclasses import dataclass
from threading import Lock

import zmq

from src.multithreading import launch_thread


@dataclass
class Order:
    pv1_required: int
    pv2_required: int
    pv3_required: int
    pv4_required: int
    pv5_required: int

    @staticmethod
    def generate_random() -> Order:
        return Order(
            pv1_required=random.randint(100, 250),
            pv2_required=random.randint(100, 250),
            pv3_required=random.randint(100, 250),
            pv4_required=random.randint(100, 250),
            pv5_required=random.randint(100, 250),
        )

    @staticmethod
    def generate_empty() -> Order:
        return Order(
            pv1_required=0,
            pv2_required=0,
            pv3_required=0,
            pv4_required=0,
            pv5_required=0,
        )

    def is_satisfied(self, quantities: dict[int, int]) -> bool:
        pv1 = quantities[1]
        pv2 = quantities[2]
        pv3 = quantities[3]
        pv4 = quantities[4]
        pv5 = quantities[5]
        return (
            pv1 >= self.pv1_required
            and pv2 >= self.pv2_required
            and pv3 >= self.pv3_required
            and pv4 >= self.pv4_required
            and pv5 >= self.pv5_required
        )


class Store:
    _product_socket: zmq.Socket
    _monitor_socket: zmq.Socket
    _factory1_socket: zmq.Socket
    _factory2_socket: zmq.Socket
    _quantities: dict[int, int]
    _quantities_lock: Lock
    _current_order = Order

    def __init__(self):
        context = zmq.Context.instance()

        self._quantities_lock = Lock()
        self._quantities = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        self._product_socket = context.socket(zmq.PULL)
        self._product_socket.bind("tcp://*:5000")

        self._monitor_socket = context.socket(zmq.REP)
        self._monitor_socket.bind("tcp://*:6000")

        self._factory1_socket = context.socket(zmq.PUSH)
        self._factory1_socket.connect("tcp://factory1:5000")

        self._factory2_socket = context.socket(zmq.PUSH)
        self._factory2_socket.connect("tcp://factory2:5000")

        self._current_order = Order.generate_empty()

    def run(self):
        launch_thread(task=self.monitor_thread)
        launch_thread(task=self.supply_thread)

        while True:
            # Start of day
            self._current_order = Order.generate_random()

            self._factory1_socket.send_string("60;60;60;60;60")

            with self._quantities_lock:
                pv1 = max(self._current_order.pv1_required - self._quantities[1], 0)
                pv2 = max(self._current_order.pv2_required - self._quantities[2], 0)
                pv3 = max(self._current_order.pv3_required - self._quantities[3], 0)
                pv4 = max(self._current_order.pv4_required - self._quantities[4], 0)
                pv5 = max(self._current_order.pv5_required - self._quantities[5], 0)

            self._factory2_socket.send_string(f"{pv1};{pv2};{pv3};{pv4};{pv5}")

            while not self._current_order.is_satisfied(self._quantities):
                pass

            # Order finished
            with self._quantities_lock:
                self._quantities[1] -= self._current_order.pv1_required
                self._quantities[2] -= self._current_order.pv2_required
                self._quantities[3] -= self._current_order.pv3_required
                self._quantities[4] -= self._current_order.pv4_required
                self._quantities[5] -= self._current_order.pv5_required

    def supply_thread(self):
        while True:
            quantity, item_type = self._product_socket.recv_string().split(":")
            quantity = int(quantity)
            item_type = int(item_type)

            with self._quantities_lock:
                self._quantities[item_type] += quantity

    def monitor_thread(self):
        while True:
            _ = self._monitor_socket.recv()
            response = ""

            with self._quantities_lock:
                response += f"{self._quantities[1]}/{self._current_order.pv1_required};"
                response += f"{self._quantities[2]}/{self._current_order.pv2_required};"
                response += f"{self._quantities[3]}/{self._current_order.pv3_required};"
                response += f"{self._quantities[4]}/{self._current_order.pv4_required};"
                response += f"{self._quantities[5]}/{self._current_order.pv5_required}"

            self._monitor_socket.send_string(response)
