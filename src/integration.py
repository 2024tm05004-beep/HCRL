import pandas as pd
import json
from datetime import datetime

class AlertCorrelator:
    """
    Correlates alerts from multiple layers (CAN and Telematics) to increase confidence.
    Maps detections to MITRE ATT&CK for Automotive.
    """
    
    # MITRE ATT&CK for Automotive Mapping
    MITRE_MAP = {
        'DoS': 'T0855 (Unauthorized Command Message)',
        'Fuzzy': 'T0830 (Adversary-in-the-Middle)',
        'Spoofing': 'T0843 (Replay Attack)',
        'Behavioral': 'T0828 (Loss of Control)'
    }

    @staticmethod
    def correlate(can_alerts, tele_alerts, window_ms=500):
        """
        Temporally correlates CAN alerts with Telematics anomalies.
        can_alerts: DataFrame with ['Timestamp', 'Attack_Type']
        tele_alerts: DataFrame with ['Timestamp', 'Anomaly_Score']
        """
        # 1. Standardize timestamps to milliseconds for windowed join
        can_alerts['Time_MS'] = (can_alerts['Timestamp'] * 1000).astype(int)
        tele_alerts['Time_MS'] = (tele_alerts['Timestamp'] * 1000).astype(int)
        
        # 2. Merge alerts by time window
        correlated = pd.merge_asof(
            can_alerts.sort_values('Time_MS'),
            tele_alerts.sort_values('Time_MS'),
            on='Time_MS',
            tolerance=window_ms,
            direction='nearest'
        )
        
        # 3. Calculate Confidence Score
        # Base: 1 (Single source) -> 2 (Multi-source overlap)
        correlated['Confidence'] = 1
        correlated.loc[correlated['Anomaly_Score'] > 0, 'Confidence'] = 2
        
        # 4. Determine Severity
        correlated['Severity'] = 'Informational'
        correlated.loc[correlated['Confidence'] == 1, 'Severity'] = 'Suspicious'
        correlated.loc[correlated['Confidence'] == 2, 'Severity'] = 'Critical'
        
        return correlated

    @staticmethod
    def generate_vsoc_alert(row, vehicle_id="VEHICLE_001"):
        """Generates a standardized vSOC alert in JSON format."""
        # Use Timestamp from CAN alerts (typically suffixed as Timestamp_x after merge)
        ts = row.get('Timestamp_x', row.get('Timestamp', 0))
        attack_type = row.get('Attack_Type', 'Unknown')
        mitre_id = AlertCorrelator.MITRE_MAP.get(attack_type, 'Unknown')
        
        alert = {
            "timestamp": datetime.fromtimestamp(ts).isoformat(),
            "vehicle_id": vehicle_id,
            "severity": str(row['Severity']),
            "confidence": int(row['Confidence']),
            "source": "Multi-Layer IDS (CAN + Telematics)",
            "mitre_mapping": str(mitre_id),
            "details": {
                "can_anomaly": True,
                "behavioral_deviation": bool(row.get('Anomaly_Score', 0) > 0)
            }
        }
        return alert
