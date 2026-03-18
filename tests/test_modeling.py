import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import CANParser
from src.features import CANFeatureEngineer
from src.validation import DataSplitter
from src.models import CANModelTrainer
from src.evaluation import IDSEvaluator

def test_model_pipeline():
    print("Testing Complete Model Pipeline (Small Scale)...")
    file_path = 'Data/DoS_dataset.csv'
    
    # 1. Pipeline: Parse -> Features -> Split
    chunk_gen = CANParser.load_csv(file_path, chunksize=5000)
    df = next(chunk_gen)
    df = CANParser.preprocess_df(df)
    df = CANFeatureEngineer.extract_message_features(df)
    df = CANFeatureEngineer.extract_window_features(df, window_size=50)
    
    X, y = CANFeatureEngineer.get_feature_matrix(df)
    X_train, X_test, y_train, y_test = DataSplitter.temporal_split(X, y, test_size=0.2)
    
    # 2. Train XGBoost Model
    print("Training XGBoost...")
    trainer = CANModelTrainer(model_type='xgboost')
    trainer.train(X_train, y_train)
    
    # 3. Evaluate
    print("Evaluating metrics...")
    y_pred = trainer.predict(X_test)
    metrics = IDSEvaluator.calculate_metrics(y_test, y_pred)
    latency = IDSEvaluator.measure_latency(trainer.model, X_test, window_size=100)
    
    print(f"Metrics: {metrics}")
    print(f"Inference Latency (100 messages): {latency:.2f}ms")
    
    # Assertions
    assert 'TPR' in metrics and 'FPR' in metrics, "Standard metrics missing"
    assert latency < 100, "Latency excessively high for a small window" # Broad check for now
    
    # 4. Serialize
    model_path = 'models/test_xgb.joblib'
    trainer.save_model(model_path)
    assert os.path.exists(model_path), "Model serialization failed"
    print("Modeling Pipeline: PASS\n")

if __name__ == "__main__":
    test_model_pipeline()
