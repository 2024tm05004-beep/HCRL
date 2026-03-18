import os
import time
import tracemalloc
import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from src.models import CANModelTrainer

class ModelProfiler:
    """
    Profiles automotive models for deployment constraints: size, memory, and throughput.
    """
    
    @staticmethod
    def get_serialized_size(file_path):
        """Returns the size of the model file in KB."""
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / 1024
        return 0

    @staticmethod
    def profile_inference(model, X_sample):
        """
        Profiles peak memory usage and throughput.
        """
        tracemalloc.start()
        start_time = time.time()
        
        # Perform inference
        model.predict(X_sample)
        
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        total_time = end_time - start_time
        num_msgs = len(X_sample)
        throughput = num_msgs / total_time if total_time > 0 else 0
        
        return {
            'peak_ram_kb': peak / 1024,
            'inference_time_ms': total_time * 1000,
            'throughput_mps': throughput
        }

class LightweightModelTrainer(CANModelTrainer):
    """
    Implements a lightweight alternative (shallow Decision Tree).
    """
    def __init__(self, max_depth=5):
        self.model_type = 'decision_tree'
        self.model = DecisionTreeClassifier(max_depth=max_depth)
