import pandas as pd
import re
import os

class CANParser:
    """
    Unified CAN Bus Parser for HCRL Automotive Datasets.
    Handles both HCRL CSV (Attack) and Raw Text (Normal) formats.
    """
    
    # Mapping for HCRL CSV columns
    CSV_COLS = ['Timestamp', 'CAN_ID', 'DLC', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Flag']
    
    # Regex for raw log format (normal_run_data.txt)
    # Example: "Timestamp: 1479121434.850202        ID: 0350    000    DLC: 8    05 28 84 66 6d 00 00 a2"
    RAW_LOG_PATTERN = re.compile(
        r'Timestamp:\s+(?P<Timestamp>[\d\.]+)\s+ID:\s+(?P<CAN_ID>[0-9a-fA-F]+)\s+\d+\s+DLC:\s+(?P<DLC>\d+)\s+(?P<Data>.*)'
    )

    @staticmethod
    def _parse_csv_line(line):
        """Helper to parse a single CSV line with variable DLC."""
        parts = line.strip().split(',')
        if len(parts) < 4:
            return None
        
        timestamp = float(parts[0])
        can_id = parts[1]
        dlc = int(parts[2])
        # Data bytes are parts[3] to parts[3+dlc-1]
        data = parts[3:3+dlc]
        # Flag is the last part
        flag = parts[-1]
        
        # Pad data to 8 bytes
        padded_data = data + ['00'] * (8 - dlc)
        return [timestamp, can_id, dlc] + padded_data + [flag]

    @staticmethod
    def load_csv(file_path, chunksize=100000):
        """
        Loads HCRL CSV datasets. Handles rows with variable DLC.
        Yields DataFrames of size chunksize.
        """
        def chunk_generator():
            with open(file_path, 'r') as f:
                chunk = []
                for line in f:
                    parsed = CANParser._parse_csv_line(line)
                    if parsed:
                        chunk.append(parsed)
                        if len(chunk) >= chunksize:
                            yield pd.DataFrame(chunk, columns=CANParser.CSV_COLS)
                            chunk = []
                if chunk:
                    yield pd.DataFrame(chunk, columns=CANParser.CSV_COLS)
        
        return chunk_generator()

    @staticmethod
    def load_consolidated(file_path, chunksize=100000):
        """
        Loads the consolidated dataset (CSV with header and attack_type column).
        Yields DataFrames of size chunksize.
        """
        return pd.read_csv(file_path, chunksize=chunksize)

    @staticmethod
    def parse_raw_text(file_path, max_lines=None):
        """
        Parses raw text logs (normal_run_data.txt) into a DataFrame.
        Note: Normal run data lacks the 'Flag' column (all 'R').
        """
        data = []
        count = 0
        with open(file_path, 'r') as f:
            for line in f:
                match = CANParser.RAW_LOG_PATTERN.match(line.strip())
                if match:
                    row = match.groupdict()
                    # Split Data payload into 8 bytes
                    data_bytes = row['Data'].split()
                    # Ensure 8 bytes (pad with 00 if needed)
                    for i in range(8):
                        row[f'D{i}'] = data_bytes[i] if i < len(data_bytes) else '00'
                    
                    row['Flag'] = 'R'  # Normal run data is all 'R'
                    del row['Data']
                    data.append(row)
                    count += 1
                
                if max_lines and count >= max_lines:
                    break
        
        df = pd.DataFrame(data)
        df['Timestamp'] = df['Timestamp'].astype(float)
        df['DLC'] = df['DLC'].astype(int)
        return df

    @staticmethod
    def preprocess_df(df):
        """
        Standardizes types for analysis.
        Converts CAN_ID and Data bytes to integers (base 16).
        """
        df['CAN_ID_INT'] = df['CAN_ID'].apply(lambda x: int(x, 16))
        for i in range(8):
            df[f'D{i}_INT'] = df[f'D{i}'].apply(lambda x: int(x, 16) if isinstance(x, str) and x else 0)
        return df
