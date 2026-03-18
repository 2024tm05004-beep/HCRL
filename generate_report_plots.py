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
    
    # 1. CAN Timing Analysis (DoS)
    df = next(CANParser.load_csv('Data/DoS_dataset.csv', chunksize=10000))
    df = CANParser.preprocess_df(df)
    df = CANFeatureEngineer.extract_message_features(df)
    
    # Save Timing Plot
    plt.figure(figsize=(12, 6))
    IDSPlotter.plot_attack_patterns(df.iloc[1000:3000], title="DoS Attack Manifestation (Timing Intervals)")
    plt.savefig('plots/timing_analysis.png', bbox_inches='tight')
    plt.close()
    
    # 2. Confusion Matrix (XGBoost)
    df = CANFeatureEngineer.extract_window_features(df, window_size=50)
    X, y = CANFeatureEngineer.get_feature_matrix(df)
    X_train, X_test, y_train, y_test = DataSplitter.temporal_split(X, y, test_size=0.2)
    trainer = CANModelTrainer(model_type='xgboost')
    trainer.train(X_train, y_train)
    y_pred = trainer.predict(X_test)
    
    plt.figure(figsize=(6, 5))
    IDSPlotter.plot_confusion_matrix(y_test, y_pred, title="Model Accuracy: DoS Confusion Matrix")
    plt.savefig('plots/confusion_matrix.png', bbox_inches='tight')
    plt.close()
    
    # 3. Behavioral Envelope (Normal Run)
    norm_df = CANParser.parse_raw_text('Data/normal_run_data/normal_run_data.txt', max_lines=5000)
    norm_df = CANParser.preprocess_df(norm_df)
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
