import pandas as pd
import os
from src.parser import CANParser

def consolidate():
    data_dir = 'Data'
    output_file = os.path.join(data_dir, 'consolidated_dataset.csv')
    
    # Define attack datasets and their labels
    datasets = [
        ('DoS_dataset.csv', 'DoS'),
        ('Fuzzy_dataset.csv', 'Fuzzy'),
        ('gear_dataset.csv', 'Spoofing'),
        ('RPM_dataset.csv', 'Spoofing'),
    ]
    
    all_dfs = []
    
    # 1. Load Attack Datasets (Sampling for manageable file size)
    for filename, attack_type in datasets:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {filename} not found in {data_dir}. Skipping.")
            continue
            
        print(f"Loading {filename}...")
        chunk_gen = CANParser.load_csv(file_path, chunksize=50000)
        df = next(chunk_gen)
        df['attack_type'] = attack_type
        all_dfs.append(df)
        print(f"Added {len(df)} rows from {filename}")

    # 2. Load Normal Dataset
    normal_path = os.path.join(data_dir, 'normal_run_data/normal_run_data.txt')
    if os.path.exists(normal_path):
        print("Loading normal_run_data.txt...")
        normal_df = CANParser.parse_raw_text(normal_path, max_lines=50000)
        normal_df['attack_type'] = 'Normal'
        all_dfs.append(normal_df)
        print(f"Added {len(normal_df)} rows from normal_run_data.txt")

    if not all_dfs:
        print("Error: No data files found. Please ensure HCRL datasets are in the Data/ directory.")
        return

    # 3. Combine and Sort
    print("Combining and sorting by Timestamp...")
    consolidated_df = pd.concat(all_dfs, ignore_index=True)
    consolidated_df = consolidated_df.sort_values('Timestamp')
    
    # 4. Save
    os.makedirs(data_dir, exist_ok=True)
    consolidated_df.to_csv(output_file, index=False)
    print(f"✅ Consolidated dataset saved to {output_file}")

if __name__ == "__main__":
    consolidate()
