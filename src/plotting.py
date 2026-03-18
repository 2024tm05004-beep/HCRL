import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve
import pandas as pd
import numpy as np

class IDSPlotter:
    """
    Standardized plotting utilities for Automotive IDS results and analysis.
    """
    
    @staticmethod
    def plot_attack_patterns(df, title="CAN Timing Analysis"):
        """Plots message timing (Delta T) to show attack manifestations."""
        plt.figure(figsize=(15, 6))
        sns.lineplot(data=df, x='Timestamp', y='Delta_T', hue='Flag', alpha=0.7)
        plt.title(title)
        plt.ylabel("Delta T (seconds)")
        plt.xlabel("Timestamp (Unix)")
        plt.yscale('log') # Use log scale to see micro-second injections
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.show()

    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, title="Confusion Matrix"):
        """Generates a heatmap of the confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Normal', 'Attack'], 
                    yticklabels=['Normal', 'Attack'])
        plt.title(title)
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.show()

    @staticmethod
    def plot_roc_curve(y_true, y_probs, title="ROC Curve"):
        """Plots the Receiver Operating Characteristic curve."""
        fpr, tpr, _ = roc_curve(y_true, y_probs)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.show()

    @staticmethod
    def plot_behavioral_envelope(tele_df, anomalies, col='Speed', title="Behavioral Anomaly Detection"):
        """Plots telematics features with anomaly markers and 3-sigma bounds."""
        mean = tele_df[col].mean()
        std = tele_df[col].std()
        
        plt.figure(figsize=(15, 6))
        plt.plot(tele_df['Timestamp'], tele_df[col], label=f'Normal {col}', color='blue', alpha=0.6)
        
        # Highlight anomalies
        anomaly_pts = tele_df[anomalies > 0]
        plt.scatter(anomaly_pts['Timestamp'], anomaly_pts[col], color='red', label='Anomalies', s=20, zorder=5)
        
        # Plot 3-sigma bounds
        plt.axhline(mean + 3*std, color='green', linestyle='--', label='3-Sigma Upper')
        plt.axhline(mean - 3*std, color='green', linestyle='--', label='3-Sigma Lower')
        
        plt.title(title)
        plt.ylabel(col)
        plt.xlabel("Timestamp")
        plt.legend()
        plt.show()
