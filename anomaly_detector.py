"""
NeuroCloud - Anomaly Detection AI
Detects unusual patterns in system metrics using ML
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        """
        Initialize anomaly detector
        contamination: expected proportion of anomalies (0.1 = 10%)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'cpu_usage', 'memory_usage', 'disk_usage',
            'network_throughput', 'response_time',
            'active_connections', 'error_rate'
        ]
        
    def load_data(self, filename='data/metrics.json'):
        """Load metrics from file"""
        if not os.path.exists(filename):
            print(f"❌ No data file found at {filename}")
            return None
            
        with open(filename, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        return df
    
    def prepare_features(self, df):
        """Prepare features for model"""
        # Select only numeric features
        features = df[self.feature_columns].copy()
        
        # Handle any missing values
        features = features.fillna(features.mean())
        
        return features
    
    def train(self, df=None, filename='data/metrics.json'):
        """Train the anomaly detection model"""
        if df is None:
            df = self.load_data(filename)
            
        if df is None or len(df) < 50:
            print("❌ Need at least 50 data points to train. Collect more metrics first.")
            return False
        
        print(f"📊 Training on {len(df)} data points...")
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        print("✅ Model trained successfully!")
        return True
    
    def detect(self, metrics_dict):
        """Detect if current metrics are anomalous"""
        if not self.is_trained:
            return None, None, "Model not trained yet"
        
        # Convert dict to dataframe
        df = pd.DataFrame([metrics_dict])
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict (-1 = anomaly, 1 = normal)
        prediction = self.model.predict(X_scaled)[0]
        
        # Get anomaly score (lower = more anomalous)
        score = self.model.score_samples(X_scaled)[0]
        
        is_anomaly = prediction == -1
        
        # Identify which metrics are problematic
        problematic_metrics = []
        if is_anomaly:
            for col in self.feature_columns:
                value = metrics_dict.get(col, 0)
                if col == 'cpu_usage' and value > 85:
                    problematic_metrics.append(f"High CPU: {value:.1f}%")
                elif col == 'memory_usage' and value > 80:
                    problematic_metrics.append(f"High Memory: {value:.1f}%")
                elif col == 'response_time' and value > 1000:
                    problematic_metrics.append(f"Slow Response: {value:.0f}ms")
                elif col == 'error_rate' and value > 5:
                    problematic_metrics.append(f"High Errors: {value:.1f}%")
        
        return is_anomaly, score, problematic_metrics
    
    def save_model(self, filename='models/anomaly_detector.pkl'):
        """Save trained model to disk"""
        os.makedirs('models', exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained,
            'feature_columns': self.feature_columns
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to {filename}")
    
    def load_model(self, filename='models/anomaly_detector.pkl'):
        """Load trained model from disk"""
        if not os.path.exists(filename):
            print(f"❌ No model found at {filename}")
            return False
        
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        self.feature_columns = model_data['feature_columns']
        
        print(f"✅ Model loaded from {filename}")
        return True

def monitor_live():
    """Monitor metrics in real-time and detect anomalies"""
    detector = AnomalyDetector()
    
    # Try to load existing model
    if not detector.load_model():
        print("Training new model...")
        if not detector.train():
            print("Please run metric_generator.py first to collect data.")
            return
        detector.save_model()
    
    print("\n🔍 Starting live anomaly detection...")
    print("Monitoring metrics every 5 seconds...")
    print("Press Ctrl+C to stop\n")
    
    import time
    
    try:
        while True:
            # Load latest metrics
            df = detector.load_data()
            if df is not None and len(df) > 0:
                latest = df.iloc[-1].to_dict()
                
                # Detect anomaly
                is_anomaly, score, issues = detector.detect(latest)
                
                if is_anomaly:
                    print(f"\n⚠️  ANOMALY DETECTED! [Score: {score:.3f}]")
                    print(f"   Time: {latest['timestamp']}")
                    for issue in issues:
                        print(f"   - {issue}")
                else:
                    print(f"✓ Normal [Score: {score:.3f}] - "
                          f"CPU: {latest['cpu_usage']:.1f}% | "
                          f"Mem: {latest['memory_usage']:.1f}% | "
                          f"RT: {latest['response_time']:.0f}ms")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")

if __name__ == "__main__":
    monitor_live()