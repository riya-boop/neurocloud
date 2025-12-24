"""
NeuroCloud - Flask Backend API
Serves metrics, AI detection, and dashboard
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
import threading
import time
from datetime import datetime

from anomaly_detector import AnomalyDetector
from metric_generator import MetricGenerator

# ------------------ APP SETUP ------------------

app = Flask(__name__)
CORS(app)

# Initialize components
detector = AnomalyDetector()
generator = MetricGenerator()

# Global state
is_monitoring = True
latest_metrics = {}
system_logs = []

# ------------------ INITIALIZATION ------------------

def initialize_system():
    """Load or train anomaly detection model"""
    if not detector.load_model():
        print("⚠️ No trained model found. Training new model...")
        if detector.train():
            detector.save_model()
        else:
            print("❌ Not enough data to train model.")

def background_monitoring():
    """Generate metrics & detect anomalies continuously"""
    global latest_metrics, system_logs, is_monitoring

    while True:
        if is_monitoring:
            try:
                metrics = generator.generate_all_metrics()
                latest_metrics = metrics
                generator.save_metrics(metrics)

                if detector.is_trained:
                    is_anomaly, score, issues = detector.detect(metrics)
                    if is_anomaly:
                        system_logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "type": "warning",
                            "message": f"Anomaly detected: {', '.join(issues)}",
                            "score": float(score),
                            "metrics": metrics
                        })

                        if len(system_logs) > 100:
                            system_logs.pop(0)

            except Exception as e:
                print("Monitoring error:", e)

        time.sleep(5)

# Start background thread
threading.Thread(target=background_monitoring, daemon=True).start()
initialize_system()

# ------------------ ROUTES ------------------

@app.route("/")
def index():
    """Serve dashboard UI"""
    return send_from_directory("dashboard", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()})

@app.route("/api/status")
def status():
    state = "healthy"
    if latest_metrics:
        if (latest_metrics.get("cpu_usage", 0) > 90 or
            latest_metrics.get("memory_usage", 0) > 85 or
            latest_metrics.get("response_time", 0) > 5000):
            state = "critical"
        elif (latest_metrics.get("cpu_usage", 0) > 70 or
              latest_metrics.get("memory_usage", 0) > 70):
            state = "warning"

    return jsonify({
        "success": True,
        "status": state,
        "monitoring": is_monitoring,
        "model_trained": detector.is_trained
    })

@app.route("/api/metrics/current")
def current_metrics():
    return jsonify({
        "success": True,
        "data": latest_metrics
    })

@app.route("/api/metrics/history")
def metrics_history():
    if os.path.exists("data/metrics.json"):
        with open("data/metrics.json", "r") as f:
            data = json.load(f)
        return jsonify({"success": True, "data": data[-100:]})
    return jsonify({"success": True, "data": []})

@app.route("/api/logs")
def logs():
    return jsonify({
        "success": True,
        "data": system_logs[-50:]
    })

@app.route("/api/monitoring/toggle", methods=["POST"])
def toggle_monitoring():
    global is_monitoring
    is_monitoring = not is_monitoring
    return jsonify({
        "success": True,
        "monitoring": is_monitoring
    })

@app.route("/api/anomaly/inject", methods=["POST"])
def inject_anomaly():
    global latest_metrics
    anomaly_type = request.json.get("type", "cpu")
    metrics = generator.generate_all_metrics(inject_anomaly=anomaly_type)
    latest_metrics = metrics
    generator.save_metrics(metrics)

    system_logs.append({
        "timestamp": datetime.now().isoformat(),
        "type": "error",
        "message": f"Manual anomaly injected: {anomaly_type}",
        "metrics": metrics
    })

    return jsonify({"success": True, "metrics": metrics})

# ------------------ MAIN ------------------

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    print("\n" + "=" * 50)
    print("🚀 NeuroCloud Backend Server Starting...")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api")
    print("=" * 50 + "\n")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
