# metrics.py — измерение задержки распознавания
import time

class PerformanceMetrics:
    def __init__(self):
        self.latencies = []
        self.accuracy = {"correct": 0, "total": 0}
    
    def measure_latency(self, func, *args):
        """Измерение задержки выполнения команды."""
        start = time.time()
        result = func(*args)
        end = time.time()
        latency = (end - start) * 1000  # мс
        self.latencies.append(latency)
        return result, latency
    
    def get_statistics(self):
        if not self.latencies:
            return {}
        return {
            "mean_latency_ms": sum(self.latencies) / len(self.latencies),
            "max_latency_ms": max(self.latencies),
            "min_latency_ms": min(self.latencies),
            "recognition_rate": (
                self.accuracy["correct"] / self.accuracy["total"] * 100
                if self.accuracy["total"] > 0 else 0
            )
        }