# Multi-Layer Automotive Intrusion Detection System (IDS)

This project implements an end-to-end intrusion detection system for automotive CAN networks, correlating low-level bus anomalies with high-level telematics behavior.

## 🚀 Key Features
- **Multi-Attack Detection:** Unified pipeline for DoS, Fuzzy, and Spoofing (RPM/Gear) attacks.
- **Dual-Layer Monitoring:**
    - **CAN Layer:** XGBoost-based classification of message timing and payload entropy.
    - **Telematics Layer:** Behavioral profiling using both Statistical (3-Sigma) and Neural (Autoencoder) baselines.
- **vSOC Integration:** Standardized JSON alert generation mapped to **MITRE ATT&CK for Automotive**.
- **Real-Time Performance:** Engineered for <10ms inference latency to meet automotive safety standards.

---

## 🛠️ Running the Project on Other Systems

Follow these steps to set up and run the IDS pipeline on a new machine.

### 1. Prerequisites
- **Python 3.9 - 3.12** (Recommended: 3.12.3)
- **pip** (Python package manager)
- **git** (to clone the repository)

### 2. Environment Setup
Clone the repository and install the required dependencies:
```bash
git clone <repository-url>
cd HCRL
pip install -r requirements.txt
```

### 3. Data Preparation
The pipeline requires a consolidated dataset. If `Data/consolidated_dataset.csv` is missing or you have fresh HCRL logs, run the consolidation script:
```bash
# Ensure HCRL CSVs (DoS, Fuzzy, etc.) are in the Data/ folder
PYTHONPATH=. python3 src/consolidate_data.py
```
This script will merge the individual attack logs and normal driving data into a single, unified source of truth for the model.

### 4. Running the Main Pipeline
The primary interface for exploration and performance validation is the Jupyter Notebook:
```bash
# Start Jupyter Notebook
jupyter notebook Automotive_IDS_Complete.ipynb
```
Inside the notebook, you can:
- Explore timing patterns of consolidated attacks.
- Train the multi-class XGBoost model.
- Execute the Autoencoder-based behavioral profiling.
- Generate correlated vSOC alerts.

### 5. Running Automated Tests
To verify the entire system's integrity (Parser, Features, Models, etc.), use the following command:
```bash
# Execute all test suites
PYTHONPATH=. pytest tests/
```
*Alternatively, run individual tests using `python3 tests/<test_file>.py`.*

### 6. Refreshing Performance Visuals
To regenerate all technical report plots from the consolidated data:
```bash
PYTHONPATH=. python3 generate_report_plots.py
```

---

## 📊 Validated Performance Summary
- **True Positive Rate:** 99.38%
- **False Positive Rate:** 0.00%
- **Inference Latency:** 6.10ms (per 100-msg window)
- **Model size (XGB):** ~104 KB (Ideal for Edge ECU deployment)

## 📂 Project Structure
- `Data/`: Consolidated and raw HCRL datasets.
- `src/`: Core logic for parsing, feature engineering, modeling, and integration.
- `models/`: Serialized XGBoost and Autoencoder models.
- `plots/`: Performance visualizations for timing, accuracy, and behavioral envelopes.
- `tests/`: Comprehensive test suite for each pipeline stage.
- `Technical_Report.md`: In-depth analysis of results and KPIs.
