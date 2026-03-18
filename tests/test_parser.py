import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import CANParser
import pandas as pd

def test_csv_parser():
    print("Testing Consolidated CSV Parser...")
    file_path = 'Data/consolidated_dataset.csv'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Load first chunk
    chunk_gen = CANParser.load_consolidated(file_path, chunksize=5)
    df = next(chunk_gen)
    
    print(f"Columns: {df.columns.tolist()}")
    print(f"Sample Row:\n{df.iloc[0]}")
    
    # Assertions
    # Consolidated has 13 columns (12 + attack_type)
    assert len(df.columns) == 13, f"Incorrect column count: {len(df.columns)}"
    assert 'Timestamp' in df.columns
    assert 'Flag' in df.columns
    assert 'attack_type' in df.columns
    print("Consolidated CSV Parser: PASS\n")

def test_raw_text_parser():
    print("Testing Raw Text Parser (Normal Run Data)...")
    file_path = 'Data/normal_run_data/normal_run_data.txt'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    df = CANParser.parse_raw_text(file_path, max_lines=5)
    
    print(f"Columns: {df.columns.tolist()}")
    print(f"Sample Row:\n{df.iloc[0]}")
    
    # Assertions
    assert len(df.columns) == 12, "Incorrect column count for standardized output"
    assert 'Flag' in df.columns and df['Flag'].iloc[0] == 'R'
    assert isinstance(df['Timestamp'].iloc[0], float)
    print("Raw Text Parser: PASS\n")

if __name__ == "__main__":
    test_csv_parser()
    test_raw_text_parser()
