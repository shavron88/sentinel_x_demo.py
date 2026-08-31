import psutil
import time


class SystemMonitor:
    def __init__(self):
        # Warmup cpu percent call
        psutil.cpu_percent(interval=None)

    def get_stats(self) -> dict:
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except Exception:
            cpu, ram, disk = 0.0, 0.0, 0.0

        return {
            "cpu_usage_percent": round(cpu, 1),
            "ram_usage_percent": round(ram, 1),
            "disk_usage_percent": round(disk, 1),
            "timestamp": time.time()
        }


if __name__ == "__main__":
    monitor = SystemMonitor()
    time.sleep(0.1)
    print("--- System Monitor Test ---")
    print(monitor.get_stats())