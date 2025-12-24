"""
NeuroCloud - Self-Healing Engine
Automatically resolves detected issues
"""

import json
import os
import time
from datetime import datetime, timedelta
from anomaly_detector import AnomalyDetector

class HealingEngine:
    def __init__(self):
        self.detector = AnomalyDetector()
        self.healing_history = []
        self.cooldown_period = timedelta(minutes=5)
        self.last_actions = {}
        
        # Load configuration
        self.load_config()
        
        # Initialize detector
        if not self.detector.load_model():
            print("⚠️  No trained model found. Training...")
            self.detector.train()
            self.detector.save_model()
    
    def load_config(self, filename='config/config.json'):
        """Load healing configuration"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.config = json.load(f)
        else:
            # Default config
            self.config = {
                'healing': {
                    'auto_restart': True,
                    'max_restart_attempts': 3,
                    'cooldown_minutes': 5
                },
                'thresholds': {
                    'cpu_critical': 90,
                    'memory_critical': 85,
                    'response_time_critical': 5000
                }
            }
    
    def can_perform_action(self, action_type):
        """Check if action is in cooldown period"""
        if action_type not in self.last_actions:
            return True
        
        last_time = self.last_actions[action_type]
        elapsed = datetime.now() - last_time
        
        return elapsed > self.cooldown_period
    
    def log_action(self, action_type, details):
        """Log healing action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action_type,
            'details': details,
            'status': 'executed'
        }
        
        self.healing_history.append(log_entry)
        self.last_actions[action_type] = datetime.now()
        
        # Save to file
        self.save_healing_log()
        
        return log_entry
    
    def save_healing_log(self, filename='logs/healing_log.json'):
        """Save healing history to file"""
        os.makedirs('logs', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.healing_history, f, indent=2)
    
    def heal_high_cpu(self, cpu_usage):
        """Healing action for high CPU usage"""
        if not self.can_perform_action('cpu_optimization'):
            return None
        
        print(f"\n🔧 HEALING ACTION: High CPU ({cpu_usage:.1f}%)")
        print("   → Optimizing CPU-intensive processes...")
        
        # Simulated actions (in real system, these would be actual commands)
        actions_taken = [
            "Identified top CPU-consuming processes",
            "Reduced background task priority",
            "Enabled CPU throttling for non-critical services",
            "Distributed load across available cores"
        ]
        
        for action in actions_taken:
            print(f"   ✓ {action}")
            time.sleep(0.5)
        
        log = self.log_action('cpu_optimization', {
            'cpu_usage': cpu_usage,
            'actions': actions_taken
        })
        
        print("   ✅ CPU optimization complete")
        return log
    
    def heal_high_memory(self, memory_usage):
        """Healing action for high memory usage"""
        if not self.can_perform_action('memory_cleanup'):
            return None
        
        print(f"\n🔧 HEALING ACTION: High Memory ({memory_usage:.1f}%)")
        print("   → Performing memory cleanup...")
        
        actions_taken = [
            "Cleared application caches",
            "Released unused memory buffers",
            "Optimized database connection pools",
            "Restarted memory-leaking services"
        ]
        
        for action in actions_taken:
            print(f"   ✓ {action}")
            time.sleep(0.5)
        
        log = self.log_action('memory_cleanup', {
            'memory_usage': memory_usage,
            'actions': actions_taken
        })
        
        print("   ✅ Memory cleanup complete")
        return log
    
    def heal_slow_response(self, response_time):
        """Healing action for slow response times"""
        if not self.can_perform_action('performance_optimization'):
            return None
        
        print(f"\n🔧 HEALING ACTION: Slow Response ({response_time:.0f}ms)")
        print("   → Optimizing performance...")
        
        actions_taken = [
            "Enabled response caching",
            "Optimized database queries",
            "Scaled up worker processes",
            "Activated CDN for static content"
        ]
        
        for action in actions_taken:
            print(f"   ✓ {action}")
            time.sleep(0.5)
        
        log = self.log_action('performance_optimization', {
            'response_time': response_time,
            'actions': actions_taken
        })
        
        print("   ✅ Performance optimization complete")
        return log
    
    def heal_high_errors(self, error_rate):
        """Healing action for high error rates"""
        if not self.can_perform_action('error_recovery'):
            return None
        
        print(f"\n🔧 HEALING ACTION: High Error Rate ({error_rate:.1f}%)")
        print("   → Recovering from errors...")
        
        actions_taken = [
            "Analyzed error logs for patterns",
            "Restarted failing services",
            "Reset connection pools",
            "Enabled circuit breakers"
        ]
        
        for action in actions_taken:
            print(f"   ✓ {action}")
            time.sleep(0.5)
        
        log = self.log_action('error_recovery', {
            'error_rate': error_rate,
            'actions': actions_taken
        })
        
        print("   ✅ Error recovery complete")
        return log
    
    def analyze_and_heal(self, metrics):
        """Analyze metrics and apply appropriate healing"""
        # First, detect if there's an anomaly
        is_anomaly, score, issues = self.detector.detect(metrics)
        
        if not is_anomaly:
            return None
        
        print(f"\n⚠️  ANOMALY DETECTED [Score: {score:.3f}]")
        print(f"   Issues: {', '.join(issues)}")
        
        # Apply healing actions based on thresholds
        healing_actions = []
        
        cpu = metrics.get('cpu_usage', 0)
        memory = metrics.get('memory_usage', 0)
        response_time = metrics.get('response_time', 0)
        error_rate = metrics.get('error_rate', 0)
        
        if cpu > self.config['thresholds']['cpu_critical']:
            action = self.heal_high_cpu(cpu)
            if action:
                healing_actions.append(action)
        
        if memory > self.config['thresholds']['memory_critical']:
            action = self.heal_high_memory(memory)
            if action:
                healing_actions.append(action)
        
        if response_time > self.config['thresholds']['response_time_critical']:
            action = self.heal_slow_response(response_time)
            if action:
                healing_actions.append(action)
        
        if error_rate > 5:
            action = self.heal_high_errors(error_rate)
            if action:
                healing_actions.append(action)
        
        return healing_actions

def run_healing_system():
    """Run the self-healing system continuously"""
    engine = HealingEngine()
    
    print("\n🏥 NeuroCloud Self-Healing System ONLINE")
    print("=" * 50)
    print("Monitoring and auto-healing enabled...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Load latest metrics
            df = engine.detector.load_data()
            
            if df is not None and len(df) > 0:
                latest = df.iloc[-1].to_dict()
                
                # Analyze and heal if needed
                actions = engine.analyze_and_heal(latest)
                
                if actions:
                    print(f"\n📊 Healing Summary: {len(actions)} action(s) performed")
                else:
                    # Show healthy status
                    timestamp = latest['timestamp']
                    print(f"✓ [{timestamp}] System Healthy - "
                          f"CPU: {latest['cpu_usage']:.1f}% | "
                          f"Mem: {latest['memory_usage']:.1f}% | "
                          f"RT: {latest['response_time']:.0f}ms")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Healing system stopped")
        print(f"Total healing actions performed: {len(engine.healing_history)}")

if __name__ == "__main__":
    run_healing_system()