import pandas as pd
import numpy as np
import joblib
import os
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

class TelematicsProcessor:
    """
    Derives telematics-like features from CAN bus signals.
    Focuses on speed, acceleration, and behavioral profiles.
    """
    
    # Common HCRL (Kia Soul) IDs for telematics proxies
    ID_RPM = '0316'   # Often contains RPM
    ID_SPEED = '043f' # Often contains Speed
    
    @staticmethod
    def derive_features(df):
        """
        Extracts speed and RPM proxies from CAN payloads.
        Standardizes them into a 'telematics' dataframe.
        """
        # 1. Extract Speed (proxy from ID 043f, typically byte 6 or 4-5)
        # For simplicity in this assignment, we use the raw value of a data byte as a proxy
        speed_df = df[df['CAN_ID'] == TelematicsProcessor.ID_SPEED].copy()
        speed_df['Speed'] = speed_df['D6_INT'] # Proxy for vehicle speed
        
        # 2. Extract RPM (proxy from ID 0316, typically bytes 2-3)
        rpm_df = df[df['CAN_ID'] == TelematicsProcessor.ID_RPM].copy()
        rpm_df['RPM'] = rpm_df['D2_INT'] * 256 + rpm_df['D3_INT'] # Proxy for engine RPM
        
        # 3. Merge and resample to a common 1Hz (1s) time-base for telematics behavior
        # This simulates typical telematics reporting rates
        tele_df = pd.merge_asof(
            speed_df[['Timestamp', 'Speed']].sort_values('Timestamp'),
            rpm_df[['Timestamp', 'RPM']].sort_values('Timestamp'),
            on='Timestamp',
            direction='nearest'
        )
        
        # 4. Behavioral Features: Acceleration (Delta Speed / Delta Time)
        tele_df['Delta_T'] = tele_df['Timestamp'].diff().fillna(0.1)
        tele_df['Acceleration'] = tele_df['Speed'].diff() / tele_df['Delta_T']
        
        # 5. Usage Patterns: Braking Intensity (Negative acceleration)
        tele_df['Braking_Intensity'] = tele_df['Acceleration'].apply(lambda x: abs(x) if x < 0 else 0)
        
        return tele_df.dropna()

class BehavioralBaseline:
    """
    Defines 'normal' driving envelopes and detects behavioral anomalies.
    """
    
    def __init__(self):
        self.stats = {}

    def fit(self, tele_df):
        """Learns the normal driving envelope from baseline data."""
        for col in ['Speed', 'RPM', 'Acceleration', 'Braking_Intensity']:
            self.stats[col] = {
                'mean': tele_df[col].mean(),
                'std': tele_df[col].std()
            }
        print(f"Baseline learned for {list(self.stats.keys())}")

    def detect_anomalies(self, tele_df, threshold_sigma=3):
        """
        Flags deviations outside the Mean +/- N*Sigma envelope.
        Returns a series of anomaly scores.
        """
        anomaly_scores = pd.Series(0, index=tele_df.index)
        
        for col, stat in self.stats.items():
            upper = stat['mean'] + threshold_sigma * stat['std']
            lower = stat['mean'] - threshold_sigma * stat['std']
            
            # Identify points outside the envelope
            deviations = (tele_df[col] > upper) | (tele_df[col] < lower)
            anomaly_scores += deviations.astype(int)
            
        return anomaly_scores

class AutoencoderBaseline:
    """
    Learns 'normal' behavior using an Autoencoder (MLP-based).
    Detects anomalies based on high reconstruction error.
    """
    
    def __init__(self, hidden_layer_sizes=(8, 4, 8)):
        self.scaler = StandardScaler()
        # We use MLPRegressor as a simple Autoencoder (X -> X)
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes, 
            activation='relu', 
            solver='adam', 
            max_iter=500,
            random_state=42
        )
        self.threshold = 0

    def fit(self, tele_df):
        """Trains the Autoencoder on normal behavior patterns."""
        cols = ['Speed', 'RPM', 'Acceleration', 'Braking_Intensity']
        X = tele_df[cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Train to reconstruct itself
        self.model.fit(X_scaled, X_scaled)
        
        # Set threshold based on max reconstruction error in the training set
        X_pred = self.model.predict(X_scaled)
        mse = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        self.threshold = np.mean(mse) + 3 * np.std(mse) # Mean + 3 Sigma on error
        print(f"Autoencoder baseline fit. Reconstruction Threshold: {self.threshold:.4f}")

    def detect_anomalies(self, tele_df):
        """Flags samples where reconstruction error exceeds the threshold."""
        cols = ['Speed', 'RPM', 'Acceleration', 'Braking_Intensity']
        X = tele_df[cols].values
        X_scaled = self.scaler.transform(X)
        
        X_pred = self.model.predict(X_scaled)
        mse = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        
        # 1 for Anomaly, 0 for Normal
        return (mse > self.threshold).astype(int)

    def save_model(self, file_path):
        """Serializes the Autoencoder and its configuration."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = {
            'model': self.model,
            'scaler': self.scaler,
            'threshold': self.threshold
        }
        joblib.dump(data, file_path)
        print(f"Autoencoder model saved to {file_path}")

    @staticmethod
    def load_model(file_path):
        """Loads a serialized Autoencoder model."""
        data = joblib.load(file_path)
        ae = AutoencoderBaseline()
        ae.model = data['model']
        ae.scaler = data['scaler']
        ae.threshold = data['threshold']
        return ae
