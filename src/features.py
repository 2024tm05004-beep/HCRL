import pandas as pd
import numpy as np
from scipy.stats import entropy

class CANFeatureEngineer:
    """
    Feature Engineering Pipeline for CAN Bus Intrusion Detection.
    Implements message-level, sequence, and statistical features.
    """
    
    @staticmethod
    def calculate_payload_entropy(row):
        """Calculates Shannon entropy for the 8-byte data payload."""
        # Convert hex bytes (D0-D7) to a list of integers
        bytes_list = [int(row[f'D{i}'], 16) for i in range(8)]
        # Count frequency of each byte value
        _, counts = np.unique(bytes_list, return_counts=True)
        return entropy(counts, base=2)

    @staticmethod
    def extract_message_features(df):
        """Extracts timing intervals and payload entropy."""
        # Ensure data is sorted by timestamp for temporal analysis
        df = df.sort_values('Timestamp').reset_index(drop=True)
        
        # 1. Timing Intervals (Delta T) per CAN ID
        df['Delta_T'] = df.groupby('CAN_ID')['Timestamp'].diff().fillna(0)
        
        # 2. Payload Entropy
        # For performance on large datasets, we apply this row-wise (can be slow, optimizing later if needed)
        # Optimization: Only calculate for unique payloads if many repeats exist
        df['Payload_Entropy'] = df.apply(CANFeatureEngineer.calculate_payload_entropy, axis=1)
        
        return df

    @staticmethod
    def extract_window_features(df, window_size=100):
        """
        Extracts statistical and sequence features using sliding windows.
        window_size: Number of messages per window.
        """
        # 1. Rolling Statistics for Delta T
        df['Rolling_Mean_DT'] = df['Delta_T'].rolling(window=window_size).mean()
        df['Rolling_Std_DT'] = df['Delta_T'].rolling(window=window_size).std()
        
        # 2. ID Frequency (Count of unique IDs in window)
        # Use CAN_ID_INT for pandas rolling compatibility
        df['Unique_IDs_In_Window'] = df['CAN_ID_INT'].rolling(window=window_size).apply(lambda x: len(np.unique(x)), raw=True)
        
        # 3. ID Transition (N-grams)
        df['Prev_CAN_ID'] = df['CAN_ID'].shift(1)
        df['ID_Transition'] = df['Prev_CAN_ID'].fillna('START') + "_" + df['CAN_ID']
        
        return df.dropna()

    @staticmethod
    def get_feature_matrix(df):
        """Returns the final feature matrix and labels for modeling."""
        # Select numeric features for ML models
        feature_cols = [
            'CAN_ID_INT', 'DLC', 'Delta_T', 'Payload_Entropy', 
            'Rolling_Mean_DT', 'Rolling_Std_DT', 'Unique_IDs_In_Window'
        ]
        
        X = df[feature_cols]
        # Map 'T' -> 1 (Attack), 'R' -> 0 (Normal)
        y = (df['Flag'] == 'T').astype(int)
        
        return X, y
