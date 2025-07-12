import curses
from time import sleep

import zmq


def run_monitor():
    curses.wrapper(_run_monitor)


def get_warehouse_info(socket: zmq.Socket) -> tuple[str, str]:
    socket.send(b"*")
    data = socket.recv_string().split(":")
    return data[0], data[1]


def get_assembly_lines_info(socket: zmq.Socket) -> list[tuple[str, str]]:
    socket.send(b"*")
    data = socket.recv_string()
    info = []
    for line in data.split(";"):
        line = line.split(":")
        info.append((line[0], line[1]))

    return info


def get_store_info(socket: zmq.Socket) -> list[tuple[str, str]]:
    socket.send(b"*")
    data = socket.recv_string()
    info = []
    for product in data.split(";"):
        product = product.split("/")
        info.append((product[0], product[1]))

    return info


def _run_monitor(stdscr: curses.window):
    stdscr.clear()
    curses.curs_set(0)

    colors = {"RED": 1, "YELLOW": 2, "GREEN": 3}
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    context = zmq.Context.instance()
    warehouse_socket: zmq.Socket = context.socket(zmq.REQ)
    warehouse_socket.connect("tcp://localhost:6000")
    factory1_socket: zmq.Socket = context.socket(zmq.REQ)
    factory1_socket.connect("tcp://localhost:6001")

    store_socket: zmq.Socket = context.socket(zmq.REQ)
    store_socket.connect("tcp://localhost:6003")

    while True:
        stdscr.erase()

        qty, status = get_warehouse_info(warehouse_socket)
        stdscr.addstr(
            0, 0, f"Almoxarifado: {qty} partes", curses.color_pair(colors[status])
        )

        stdscr.addstr(2, 0, "Fábrica 1")
        info = get_assembly_lines_info(factory1_socket)
        for i, (qty, status) in enumerate(info):
            stdscr.addstr(
                3 + i,
                4,
                f"> Linha {i+1}: {qty} partes",
                curses.color_pair(colors[status]),
            )

        stdscr.addstr(16, 0, "Depósito")
        info = get_store_info(store_socket)
        for i, (current, requested) in enumerate(info):
            stdscr.addstr(17 + i, 4, f"> Pv{i+1}: {current} / {requested}")

        stdscr.refresh()
