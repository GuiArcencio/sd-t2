import zmq

from src.entities.assemblyline import AssemblyLine
from src.multithreading import launch_thread


class Factory:
    _lines: list[AssemblyLine]
    _request_socket: zmq.Socket
    _monitor_socket: zmq.Socket

    def __init__(self, num_lines: int, supplier_hostname: str, supplier_port: int):
        context = zmq.Context.instance()

        self._lines = list()
        for i in range(num_lines):
            self._lines.append(
                AssemblyLine(
                    id=str(i),
                    supplier_hostname=supplier_hostname,
                    supplier_port=supplier_port,
                )
            )

        self._request_socket = context.socket(zmq.PULL)
        self._request_socket.bind("tcp://*:5000")

        self._monitor_socket = context.socket(zmq.REP)
        self._monitor_socket.bind("tcp://*:6000")

    def run(self):
        for line in self._lines:
            launch_thread(line.run)

        launch_thread(task=self.monitor_thread)

        while True:
            request = self._request_socket.recv_string().split(";")
            for item_type, items in enumerate(request):
                items = int(items)
                if items > 0:
                    quotient = items // len(self._lines)
                    remainder = items % len(self._lines)
                    for i, line in enumerate(self._lines):
                        line.request(
                            item_type + 1, quotient + (1 if i < remainder else 0)
                        )

    def monitor_thread(self):
        while True:
            _ = self._monitor_socket.recv()
            response = ""
            for line in self._lines:
                quantity_available, status = line._stock.get_quantity()
                response += f"{quantity_available}:{status};"

            self._monitor_socket.send_string(response.strip(";"))
