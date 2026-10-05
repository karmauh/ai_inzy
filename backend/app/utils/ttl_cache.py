import copy
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Hashable, Optional


class TTLCache:
    """
    Prosty, bezpieczny wątkowo cache w pamięci z czasem życia wpisów i limitem rozmiaru (usuwane najstarsze).
    Zwraca głębokie kopie, aby modyfikacja wyniku przez wywołującego nie zmieniała zawartości cache.
    """

    def __init__(self, ttl_seconds: float, max_entries: int = 128, clock: Callable[[], float] = time.monotonic):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._clock = clock
        self._entries: "OrderedDict[Hashable, tuple]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: Hashable) -> Optional[Any]:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            stored_at, value = entry
            if self._clock() - stored_at > self.ttl_seconds:
                del self._entries[key]
                return None
            self._entries.move_to_end(key)
            return copy.deepcopy(value)

    def set(self, key: Hashable, value: Any) -> None:
        with self._lock:
            self._entries[key] = (self._clock(), copy.deepcopy(value))
            self._entries.move_to_end(key)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
