from collections.abc import Callable
from threading import Lock, Thread, Timer


def launch_thread(task: Callable, *args, **kwargs) -> Thread:
    thread = Thread(target=task, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def delay_thread(task: Callable, timeout: float, *args, **kwargs) -> Timer:
    thread = Timer(interval=timeout, function=task, args=args, kwargs=kwargs)
    thread.start()
    return thread


class AtomicValue[T]:
    """
    Multithreading utility for using atomic operations on a value
    """

    _value: T
    _lock: Lock

    def __init__(self, initial_value: T):
        self._value = initial_value
        self._lock = Lock()

    def get(self) -> T:
        with self._lock:
            return self._value

    def set(self, value: T):
        with self._lock:
            self._value = value

    def update(self, update_func: Callable[[T], T]) -> tuple[T, T]:
        with self._lock:
            old_value = self._value
            self._value = update_func(self._value)
            return old_value, self._value
