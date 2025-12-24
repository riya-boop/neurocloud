"""
NeuroCloud - Metric Generator
Simulates realistic system metrics for testing
"""

import random
import time
import json
import os
from datetime import datetime
import math

class MetricGenerator:
    def __init__(self):
        self.time_step = 0
        self.base_values = {
            'cpu': 40,
            'memory': 50,
            'disk': 60,
            'network': 100,
            'response_time': 200
        }
        
    def generate_cpu(self):
        """Generate CPU usage (0-100%)"""
        # Normal pattern with occasional spikes
        base = self.base_values['cpu']
        noise = random.gauss(0, 5)
        spike = 30 if random.random() < 0.05 else 0  # 5% chance of spike
        value = base + noise + spike
        return max(0, min(100, value))
    
    def generate_memory(self):
        """Generate memory usage (0-100%)"""
        base = self.base_values['memory']
        # Slowly increasing trend (memory leak simulation)
        trend = self.time_step * 0.01
        noise = random.gauss(0, 3)
        value = base + trend + noise
        
        # Reset if too high (simulating restart)
        if value > 95:
            self.base_values['memory'] = 50
            return 50
        return max(0, min(100, value))
    
    def generate_disk(self):
        """Generate disk usage (0-100%)"""
        base = self.base_values['disk']
        # Very slow growth
        trend = self.time_step * 0.005
        noise = random.gauss(0, 2)
        value = base + trend + noise
        return max(0, min(100, value))
    
    def generate_network(self):
        """Generate network throughput (Mbps)"""
        # Cyclical pattern (simulating daily traffic)
        cycle = 50 * math.sin(self.time_step * 0.1) + 50
        noise = random.gauss(0, 10)
        value = cycle + noise
        return max(0, value)
    
    def generate_response_time(self):
        """Generate API response time (ms)"""
        base = self.base_values['response_time']
        noise = random.gauss(0, 20)
        
        # Occasional latency spikes
        spike = 1000 if random.random() < 0.03 else 0
        value = base + noise + spike
        return max(0, value)
    
    def inject_anomaly(self, metric_type):
        """Inject an anomaly for testing"""
        if metric_type == 'cpu':
            return 95 + random.uniform(0, 5)
        elif metric_type == 'memory':
            return 90 + random.uniform(0, 10)
        elif metric_type == 'response_time':
            return 4000 + random.uniform(0, 1000)
        return None
    
    def generate_all_metrics(self, inject_anomaly=None):
        """Generate all metrics at once"""
        self.time_step += 1
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': self.generate_cpu(),
            'memory_usage': self.generate_memory(),
            'disk_usage': self.generate_disk(),
            'network_throughput': self.generate_network(),
            'response_time': self.generate_response_time(),
            'active_connections': random.randint(50, 200),
            'error_rate': random.uniform(0, 2)  # percentage
        }
        
        # Inject anomaly if requested
        if inject_anomaly:
            anomaly_value = self.inject_anomaly(inject_anomaly)
            if anomaly_value:
                metrics[inject_anomaly] = anomaly_value
        
        return metrics
    
    def save_metrics(self, metrics, filename='data/metrics.json'):
        """Save metrics to file"""
        os.makedirs('data', exist_ok=True)
        
        # Load existing data
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Append new metrics
        data.append(metrics)
        
        # Keep only last 1000 entries
        if len(data) > 1000:
            data = data[-1000:]
        
        # Save back
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    """Run continuous metric generation"""
    generator = MetricGenerator()
    print("🚀 NeuroCloud Metric Generator Started")
    print("Generating metrics every 5 seconds...")
    print("Press Ctrl+C to stop\n")
    
    iteration = 0
    try:
        while True:
            iteration += 1
            
            # Inject anomaly every 50 iterations for testing
            inject = None
            if iteration % 50 == 0:
                inject = random.choice(['cpu', 'memory', 'response_time'])
                print(f"⚠️  Injecting {inject} anomaly for testing...")
            
            # Generate metrics
            metrics = generator.generate_all_metrics(inject_anomaly=inject)
            
            # Save to file
            generator.save_metrics(metrics)
            
            # Display current metrics
            print(f"[{metrics['timestamp']}]")
            print(f"  CPU: {metrics['cpu_usage']:.1f}% | "
                  f"Memory: {metrics['memory_usage']:.1f}% | "
                  f"Disk: {metrics['disk_usage']:.1f}% | "
                  f"Response: {metrics['response_time']:.0f}ms")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Metric generation stopped")

if __name__ == "__main__":
    main()