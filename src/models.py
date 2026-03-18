import joblib
import os
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix

class CANModelTrainer:
    """
    Handles training and serialization of IDS models.
    Supports supervised (XGB, RF) and unsupervised (IsoForest) approaches.
    """
    
    def __init__(self, model_type='xgboost'):
        self.model_type = model_type
        if model_type == 'xgboost':
            self.model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, n_jobs=-1)
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1)
        elif model_type == 'isolation_forest':
            self.model = IsolationForest(n_estimators=100, contamination=0.1, n_jobs=-1)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def train(self, X_train, y_train=None):
        """Trains the selected model."""
        if self.model_type == 'isolation_forest':
            self.model.fit(X_train)
        else:
            self.model.fit(X_train, y_train)
        return self.model

    def predict(self, X_test):
        """Predicts anomalies or attack classes."""
        preds = self.model.predict(X_test)
        if self.model_type == 'isolation_forest':
            # IsoForest returns -1 for anomalies, 1 for normal. 
            # Convert to 1 for Attack, 0 for Normal to match our schema.
            return [1 if p == -1 else 0 for p in preds]
        return preds

    def save_model(self, file_path):
        """Serializes the model for deployment."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        joblib.dump(self.model, file_path)
        print(f"Model saved to {file_path}")

    @staticmethod
    def load_model(file_path):
        """Loads a serialized model."""
        return joblib.load(file_path)
