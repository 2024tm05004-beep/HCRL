import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validation import DataSplitter

def test_temporal_split():
    print("Testing Temporal Splitting...")
    # 1. Mock sorted time-series data
    data = {
        'Timestamp': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Feature1': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        'Label': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    }
    df = pd.DataFrame(data)
    X = df[['Timestamp', 'Feature1']]
    y = df['Label']
    
    # 2. Perform temporal split (test_size=0.3)
    X_train, X_test, y_train, y_test = DataSplitter.temporal_split(X, y, test_size=0.3)
    
    print(f"Train set: {X_train['Timestamp'].tolist()}")
    print(f"Test set: {X_test['Timestamp'].tolist()}")
    
    # Assertions
    assert len(X_train) == 7, "Incorrect train size"
    assert len(X_test) == 3, "Incorrect test size"
    assert X_train['Timestamp'].max() < X_test['Timestamp'].min(), "Temporal leakage detected!"
    
    # Integrity check
    assert DataSplitter.validate_split(X_train, X_test), "Validation check failed"
    print("Temporal Split: PASS\n")

if __name__ == "__main__":
    test_temporal_split()
