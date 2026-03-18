import time
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

class IDSEvaluator:
    """
    Calculates automotive security metrics: TPR, FPR, F1, and Inference Latency.
    """
    
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        """
        Calculates TPR, FPR, and F1.
        TPR = TP / (TP + FN)
        FPR = FP / (FP + TN)
        """
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        f1 = f1_score(y_true, y_pred)
        
        return {
            'TPR': tpr,
            'FPR': fpr,
            'F1': f1,
            'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp
        }

    @staticmethod
    def measure_latency(model, X_test, window_size=100):
        """
        Measures inference latency for a single 100-message window.
        Requirement: < 20-30ms per window.
        """
        # Select a sample window
        sample = X_test.iloc[:window_size]
        
        start_time = time.time()
        model.predict(sample)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        return latency_ms
