import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
sys.path.append(os.getcwd())

from src.parser import CANParser
from src.features import CANFeatureEngineer
from src.validation import DataSplitter
from src.models import CANModelTrainer
from src.telematics import TelematicsProcessor, BehavioralBaseline
from src.plotting import IDSPlotter

def generate_report_plots():
    print("Generating plots for Technical Report...")
    
    # 1. CAN Timing Analysis (Consolidated Data - DoS sample)
    consolidated_file = 'Data/consolidated_dataset.csv'
    df = next(CANParser.load_consolidated(consolidated_file, chunksize=20000))
    df = CANParser.preprocess_df(df)
    df = CANFeatureEngineer.extract_message_features(df)
    
    # Save Timing Plot (using DoS subset if available in this chunk)
    plt.figure(figsize=(12, 6))
    dos_sample = df[df['attack_type'] == 'DoS']
    if len(dos_sample) > 2000:
        plot_df = dos_sample.iloc[1000:3000]
    else:
        plot_df = df.iloc[1000:3000]
        
    IDSPlotter.plot_attack_patterns(plot_df, title="Multi-Attack Dataset: Injection Timing Intervals")
    plt.savefig('plots/timing_analysis.png', bbox_inches='tight')
    plt.close()
    
    # 2. Confusion Matrix (XGBoost - Multi-Attack)
    df = CANFeatureEngineer.extract_window_features(df, window_size=50)
    X, y = CANFeatureEngineer.get_feature_matrix(df)
    X_train, X_test, y_train, y_test = DataSplitter.temporal_split(X, y, test_size=0.2)
    trainer = CANModelTrainer(model_type='xgboost')
    trainer.train(X_train, y_train)
    y_pred = trainer.predict(X_test)
    
    plt.figure(figsize=(6, 5))
    IDSPlotter.plot_confusion_matrix(y_test, y_pred, title="Model Accuracy: Multi-Attack Confusion Matrix")
    plt.savefig('plots/confusion_matrix.png', bbox_inches='tight')
    plt.close()
    
    # 3. Behavioral Envelope (Normal subset of consolidated)
    norm_df = df[df['attack_type'] == 'Normal'].copy()
    if len(norm_df) > 100:
        tele_df = TelematicsProcessor.derive_features(norm_df)
        baseline = BehavioralBaseline()
        baseline.fit(tele_df)
        anomalies = baseline.detect_anomalies(tele_df, threshold_sigma=3)
        
        plt.figure(figsize=(12, 6))
        IDSPlotter.plot_behavioral_envelope(tele_df, anomalies, col='Speed', title="Telematics Baseline: 3-Sigma Speed Envelope")
        plt.savefig('plots/behavioral_envelope.png', bbox_inches='tight')
        plt.close()
    
    print("All report plots saved successfully to plots/ directory.")

if __name__ == "__main__":
    generate_report_plots()
