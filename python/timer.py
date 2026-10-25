import time
import atexit
import signal
import threading
from collections import defaultdict


class Timer:
    # Global statistics storage
    _timers = defaultdict(list)
    _lock = threading.Lock()
    _registered = False
    _collect_stats = True

    def __init__(self, name: str = None, head_str: str = "", end_str: str = "\n"):
        self.name = name
        self.head_str = head_str
        self.start_time = time.perf_counter()
        self.end_str = end_str
        self.elapsed_time = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.elapsed_time = time.perf_counter() - self.start_time

        if Timer._collect_stats and self.name:
            Timer._add_statistic(self.name, self.elapsed_time)

        print(
            f"{self.head_str}[{self.name}] Elapsed time: {self.elapsed_time:.3f} (sec)",
            end=self.end_str,
        )

    @classmethod
    def _add_statistic(cls, name, elapsed_time):
        """Add statistic without lock overhead."""
        cls._timers[name].append(elapsed_time)

    @classmethod
    def enable_statistics(cls, enabled: bool = True):
        """Enable or disable statistics collection."""
        cls._collect_stats = enabled

        if enabled and not cls._registered:
            cls._register_exit_handlers()
            cls._registered = True

    @classmethod
    def _register_exit_handlers(cls):
        """Register handlers for program exit and interruption."""
        atexit.register(cls._print_statistics)

        def signal_handler(signum, frame):
            raise SystemExit(128 + signum)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    @classmethod
    def _print_statistics(cls):
        """Print statistics for all timers."""
        if not cls._timers:
            return

        print("\n" + "=" * 60)
        print("TIMER STATISTICS")
        print("=" * 60)

        for name, times in cls._timers.items():
            if times:
                total_time = sum(times)
                avg_time = total_time / len(times)
                min_time = min(times)
                max_time = max(times)

                print(f"{name}:")
                print(f"  Count: {len(times)}")
                print(f"  Average: {avg_time:.3f} sec")
                print(f"  Min: {min_time:.3f} sec")
                print(f"  Max: {max_time:.3f} sec")
                print(f"  Total: {total_time:.3f} sec")
                print()

        print("=" * 60)

    @classmethod
    def get_statistics(cls, name: str = None):
        """Get statistics for a specific timer or all timers."""
        if name:
            times = cls._timers.get(name, [])

            if times:
                total_time = sum(times)

                return {
                    "count": len(times),
                    "average": total_time / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": total_time,
                }

            return None

        return {
            name: cls.get_statistics(name)
            for name in cls._timers.keys()
        }

    @classmethod
    def reset_statistics(cls):
        """Reset all timer statistics."""
        with cls._lock:
            cls._timers.clear()


class SimpleTimer:
    """Lightweight timer without statistics collection."""

    def __init__(self, name: str = None, head_str: str = "", end_str: str = "\n"):
        self.name = name
        self.head_str = head_str
        self.start_time = time.perf_counter()
        self.end_str = end_str

    def __enter__(self):
        return self

    def __exit__(self, *args):
        elapsed_time = time.perf_counter() - self.start_time

        print(
            f"{self.head_str}[{self.name}] Elapsed time: {elapsed_time:.3f} (sec)",
            end=self.end_str,
        )
