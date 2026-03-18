import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import CANParser
from src.features import CANFeatureEngineer
from src.validation import DataSplitter
from src.models import CANModelTrainer
from src.deployment import ModelProfiler, LightweightModelTrainer

def test_deployment_profiling():
    print("Testing Deployment Constraints (Heavy vs. Light Comparison)...")
    
    # 1. Prepare Data
    chunk_gen = CANParser.load_consolidated('Data/consolidated_dataset.csv', chunksize=10000)
    df = next(chunk_gen)
    df = CANParser.preprocess_df(df)
    df = CANFeatureEngineer.extract_message_features(df)
    df = CANFeatureEngineer.extract_window_features(df, window_size=50)
    X, y = CANFeatureEngineer.get_feature_matrix(df)
    X_train, X_test, y_train, y_test = DataSplitter.temporal_split(X, y, test_size=0.2)
    
    # 2. Heavy Model: XGBoost
    print("Profiling Heavy Model (XGBoost)...")
    heavy_trainer = CANModelTrainer(model_type='xgboost')
    heavy_trainer.train(X_train, y_train)
    heavy_path = 'models/heavy_xgb.joblib'
    heavy_trainer.save_model(heavy_path)
    heavy_stats = ModelProfiler.profile_inference(heavy_trainer.model, X_test)
    heavy_size = ModelProfiler.get_serialized_size(heavy_path)
    
    # 3. Light Model: Decision Tree (Shallow)
    print("Profiling Light Model (Decision Tree)...")
    light_trainer = LightweightModelTrainer(max_depth=3)
    light_trainer.train(X_train, y_train)
    light_path = 'models/light_dt.joblib'
    light_trainer.save_model(light_path)
    light_stats = ModelProfiler.profile_inference(light_trainer.model, X_test)
    light_size = ModelProfiler.get_serialized_size(light_path)
    
    print(f"\nDeployment Metrics Comparison:")
    print(f"Heavy (XGBoost): Size: {heavy_size:.1f} KB, RAM: {heavy_stats['peak_ram_kb']:.1f} KB, Throughput: {heavy_stats['throughput_mps']:.0f} MPS")
    print(f"Light (DT): Size: {light_size:.1f} KB, RAM: {light_stats['peak_ram_kb']:.1f} KB, Throughput: {light_stats['throughput_mps']:.0f} MPS")
    
    # Assertions
    assert light_size < heavy_size, "Light model should be smaller than heavy model"
    assert light_stats['throughput_mps'] > 1000, f"Low throughput ({light_stats['throughput_mps']})"
    print("\nDeployment Constraints Profiling: PASS\n")

if __name__ == "__main__":
    test_deployment_profiling()
