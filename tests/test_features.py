import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import CANParser
from src.features import CANFeatureEngineer

def test_feature_extraction():
    print("Testing Feature Extraction (Small Sample of DoS)...")
    file_path = 'Data/DoS_dataset.csv'
    
    # 1. Parse small sample
    chunk_gen = CANParser.load_csv(file_path, chunksize=200)
    df = next(chunk_gen)
    df = CANParser.preprocess_df(df)
    
    # 2. Extract Message Features
    print("Extracting message-level features (Entropy, Delta T)...")
    df = CANFeatureEngineer.extract_message_features(df)
    
    # 3. Extract Window Features
    print("Extracting window features (Rolling Stats, Unique IDs)...")
    df = CANFeatureEngineer.extract_window_features(df, window_size=10)
    
    print(f"Sample Features Matrix:\n{df[['CAN_ID', 'Delta_T', 'Payload_Entropy', 'Rolling_Mean_DT']].head()}")
    
    # Assertions
    assert 'Payload_Entropy' in df.columns, "Entropy missing"
    assert 'Delta_T' in df.columns, "Timing intervals missing"
    assert 'Rolling_Mean_DT' in df.columns, "Rolling statistics missing"
    assert 'Unique_IDs_In_Window' in df.columns, "Unique ID counts missing"
    print("Feature Extraction: PASS\n")

if __name__ == "__main__":
    test_feature_extraction()
