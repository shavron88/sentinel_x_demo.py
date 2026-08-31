import os
import sys
import time
import platform
import psutil
from typing import Dict, Any

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()

    def get_uptime_seconds(self) -> float:
        """System ya Process ka uptime calculate karta hai."""
        return time.time() - self.start_time

    def get_formatted_uptime(self) -> str:
        """Uptime ko Readable format (e.g. 1d 2h 3m 4s) me convert karta hai."""
        uptime = int(self.get_uptime_seconds())
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)

    def get_gpu_stats(self) -> Dict[str, Any]:
        """
        NVIDIA GPU stats fetch karne ke liye (gputil / pynvml agar available ho).
        Fallback ke saath safely fail-proof banaya gaya hai.
        """
        gpu_info = {
            "available": False,
            "gpu_usage_percent": 0.0,
            "vram_total_mb": 0.0,
            "vram_used_mb": 0.0,
            "vram_percent": 0.0,
            "temperature_c": None,
            "name": "N/A"
        }
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_info.update({
                    "available": True,
                    "name": gpu.name,
                    "gpu_usage_percent": round(gpu.load * 100, 2),
                    "vram_total_mb": round(gpu.memoryTotal, 2),
                    "vram_used_mb": round(gpu.memoryUsed, 2),
                    "vram_percent": round(gpu.memoryUtil * 100, 2),
                    "temperature_c": gpu.temperature
                })
        except Exception:
            # NVML or GPUtil unavailable, returning fallback defaults
            pass

        return gpu_info

    def get_metrics(self) -> Dict[str, Any]:
        """
        Complete system stats collect karke dictionary return karta hai
        jise Dashboard / API par directly expose kiya ja sakta hai.
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        disk = psutil.disk_usage('/')

        # System Temperatures (Linux systems par mostly support hota hai)
        temp_c = None
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps and temps['coretemp']:
                temp_c = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps and temps['cpu_thermal']:
                temp_c = temps['cpu_thermal'][0].current
        except Exception:
            temp_c = None

        metrics = {
            "timestamp": time.time(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=None),
                "count_logical": psutil.cpu_count(logical=True),
                "count_physical": psutil.cpu_count(logical=False),
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
                "used_gb": round(psutil.virtual_memory().used / (1024 ** 3), 2),
                "percent": psutil.virtual_memory().percent,
            },
            "process_memory": {
                "rss_mb": round(memory_info.rss / (1024 * 1024), 2),
                "vms_mb": round(memory_info.vms / (1024 * 1024), 2),
            },
            "disk": {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "percent": disk.percent,
            },
            "gpu": self.get_gpu_stats(),
            "system_info": {
                "python_version": sys.version.split()[0],
                "platform": platform.system(),
                "platform_release": platform.release(),
                "architecture": platform.machine(),
                "uptime_seconds": round(self.get_uptime_seconds(), 2),
                "uptime_formatted": self.get_formatted_uptime(),
                "temperature_c": temp_c
            }
        }

        return metrics


# Standalone usage example / test execution
if __name__ == "__main__":
    import json
    monitor = SystemMonitor()
    print("--- System Monitoring Stats ---")
    print(json.dumps(monitor.get_metrics(), indent=4))