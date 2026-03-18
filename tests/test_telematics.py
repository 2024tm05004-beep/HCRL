import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import CANParser
from src.telematics import TelematicsProcessor, BehavioralBaseline, AutoencoderBaseline

def test_telematics_pipeline():
    print("Testing Telematics Behavioral Monitoring (3-Sigma)...")
    # 1. Load normal run data (Raw text)
    file_path = 'Data/normal_run_data/normal_run_data.txt'
    df = CANParser.parse_raw_text(file_path, max_lines=10000)
    df = CANParser.preprocess_df(df)
    
    # 2. Derive Telematics Features
    print("Deriving Speed/RPM features...")
    tele_df = TelematicsProcessor.derive_features(df)
    print(f"Telematics Head:\n{tele_df[['Timestamp', 'Speed', 'RPM', 'Acceleration']].head()}")
    
    # 3. Train Baseline
    print("Learning driving envelope...")
    baseline = BehavioralBaseline()
    baseline.fit(tele_df)
    
    # 4. Detect Anomalies (on the same data for now, should be 0 or low)
    anomalies = baseline.detect_anomalies(tele_df, threshold_sigma=3)
    anomaly_count = anomalies[anomalies > 0].count()
    print(f"Anomalies detected in normal data: {anomaly_count}")
    
    # Assertions
    assert 'Speed' in tele_df.columns and 'RPM' in tele_df.columns, "Derivation failed"
    assert 'Acceleration' in tele_df.columns, "Behavioral features missing"
    assert len(tele_df) > 0, "No telematics data produced"
    print("Telematics Behavioral Monitoring: PASS\n")

def test_autoencoder_pipeline():
    print("Testing Autoencoder-based Behavioral Monitoring...")
    # 1. Load normal run data
    file_path = 'Data/normal_run_data/normal_run_data.txt'
    df = CANParser.parse_raw_text(file_path, max_lines=5000)
    df = CANParser.preprocess_df(df)
    tele_df = TelematicsProcessor.derive_features(df)
    
    # 2. Fit Autoencoder
    print("Fitting Autoencoder...")
    ae = AutoencoderBaseline(hidden_layer_sizes=(4, 2, 4)) # Small for testing
    ae.fit(tele_df)
    
    # 3. Detect
    anomalies = ae.detect_anomalies(tele_df)
    anomaly_count = sum(anomalies)
    print(f"Autoencoder Anomalies detected in normal data: {anomaly_count}")
    
    # Assertions
    assert len(anomalies) == len(tele_df), "Autoencoder output size mismatch"
    print("Autoencoder Behavioral Monitoring: PASS\n")

if __name__ == "__main__":
    test_telematics_pipeline()
    test_autoencoder_pipeline()
