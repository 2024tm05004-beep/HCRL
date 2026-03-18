import sys
import os
import pandas as pd
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integration import AlertCorrelator

def test_integration_pipeline():
    print("Testing Multi-Layer Integration (Alert Correlation)...")
    
    # 1. Mock CAN Alerts
    can_alerts = pd.DataFrame({
        'Timestamp': [1478198376.389427, 1478198376.500000],
        'Attack_Type': ['DoS', 'Spoofing']
    })
    
    # 2. Mock Telematics Anomalies
    tele_alerts = pd.DataFrame({
        'Timestamp': [1478198376.389500, 1478198377.000000],
        'Anomaly_Score': [1, 0] # Overlap with DoS, but not with Spoofing (out of window)
    })
    
    # 3. Perform Correlation
    print("Correlating CAN and Telematics signals...")
    correlated = AlertCorrelator.correlate(can_alerts, tele_alerts, window_ms=100)
    
    # 4. Generate vSOC Alert for the first correlated row
    sample_alert = AlertCorrelator.generate_vsoc_alert(correlated.iloc[0])
    print(f"Generated vSOC Alert:\n{json.dumps(sample_alert, indent=2)}")
    
    # Assertions
    # First alert should have confidence 2 because of the overlap
    assert correlated.iloc[0]['Confidence'] == 2, "Correlation failed to boost confidence"
    assert correlated.iloc[0]['Severity'] == 'Critical', "Severity mapping failed"
    # Second alert should have confidence 1 (no overlap)
    assert correlated.iloc[1]['Confidence'] == 1, "Incorrect confidence boost"
    
    # Check MITRE mapping
    assert "T0855" in sample_alert['mitre_mapping'], "MITRE mapping failed for DoS"
    
    print("Multi-Layer Integration: PASS\n")

if __name__ == "__main__":
    test_integration_pipeline()
