import numpy as np
from sklearn.model_selection import TimeSeriesSplit

class DataSplitter:
    """
    Handles temporal data splitting for automotive time-series datasets.
    Ensures strict adherence to the temporal ordering mandate.
    """
    
    @staticmethod
    def temporal_split(X, y, test_size=0.2):
        """
        Splits data into train and test sets based on temporal order.
        Assumes X is already sorted by timestamp.
        """
        split_idx = int(len(X) * (1 - test_size))
        
        X_train = X.iloc[:split_idx]
        y_train = y.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        
        return X_train, X_test, y_train, y_test

    @staticmethod
    def get_time_series_cv(n_splits=5):
        """
        Returns a TimeSeriesSplit object for cross-validation.
        Prevents future data leakage into training folds.
        """
        return TimeSeriesSplit(n_splits=n_splits)

    @staticmethod
    def validate_split(X_train, X_test):
        """
        Verifies that no temporal leakage occurred.
        Assumes the original dataframe has a 'Timestamp' column if passed.
        """
        if 'Timestamp' in X_train.columns and 'Timestamp' in X_test.columns:
            max_train_time = X_train['Timestamp'].max()
            min_test_time = X_test['Timestamp'].min()
            assert max_train_time < min_test_time, f"Leakage detected! Max train time ({max_train_time}) >= Min test time ({min_test_time})"
            return True
        return True
