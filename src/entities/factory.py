from src.entities.assemblyline import AssemblyLine
from src.multithreading import launch_thread


class Factory:
    _lines: list[AssemblyLine]

    def __init__(self, num_lines: int, supplier_hostname: str, supplier_port: int):
        self._lines = list()
        for i in range(num_lines):
            self._lines.append(
                AssemblyLine(
                    id=str(i),
                    supplier_hostname=supplier_hostname,
                    supplier_port=supplier_port,
                )
            )

    def run(self):
        for line in self._lines:
            launch_thread(line.run)
            line.request(1, 60)

        while True:
            pass
