# GEMINI.md - Automotive Intrusion Detection System (IDS)

## Project Overview
This project involves building an intrusion detection system (IDS) for automotive networks, combining in-vehicle CAN bus anomaly detection with telematics behavioral monitoring. The goal is to detect attacks targeting modern connected vehicles, such as injection attacks, replay attacks, and compromised services.

## Car hacking dataset
As modern vehicles have lots of connectivity, protecting in-vehicle network from cyber-attacks becomes an important issue. Controller Area Network (CAN) is a de facto standard for the in-vehicle network. But, lack of security features of CAN protocol makes vehicles vulnerable to attacks. The message injection attack is a representative attack type which injects fabricated messages to deceive original ECUs or cause malfunctions. Thus we open our datasets to the public to foster further car security research.


1. Dataset
We provide car-hacking datasets which include DoS attack, fuzzy attack, spoofing the drive gear, and spoofing the RPM gauge. Datasets were constructed by logging CAN traffic via the OBD-II port from a real vehicle while message injection attacks were performing. Datasets contain each 300 intrusions of message injection. Each intrusion performed for 3 to 5 seconds, and each dataset has total 30 to 40 minutes of the CAN traffic.


    1.    DoS Attack : Injecting messages of ‘0000’ CAN ID every 0.3 milliseconds. ‘0000’ is the most dominant.

    2.    Fuzzy Attack : Injecting messages of totally random CAN ID and DATA values every 0.5 milliseconds.

    3.    Spoofing Attack (RPM/gear) : Injecting messages of certain CAN ID related to RPM/gear information every 1 millisecond.


1.1 Data attributes
Timestamp, CAN ID, DLC, DATA[0], DATA[1], DATA[2], DATA[3], DATA[4], DATA[5], DATA[6], DATA[7], Flag


    1.    Timestamp : recorded time (s)

    2.    CAN ID : identifier of CAN message in HEX (ex. 043f)

    3.    DLC : number of data bytes, from 0 to 8

    4.    DATA[0~7] : data value (byte)

    5.    Flag : T or R, T represents injected message while R represents normal message

     Attack Type	# of messages 	 # of normal messages	 # of injected messages
 DoS_dataset        3,665,771 	      3,078,250 	              587,521 
Fuzzy__dataset 	    3,838,860 	      3,347,013 	              491,847 

gear_dataset	    4,443,142 	      3,845,890 	              597,252 

RPM_dataset	        4,621,702	      3,966,805 	              654,897 
 
normal_run_data	    988,987 	      988,872 	                     -



## Core Mandates & Engineering Standards
- **Data Privacy:** Handle all vehicle and driver data with extreme care. Ensure privacy-preserving features for location data.
- **Real-Time Efficiency:** Models must be optimized for resource-constrained automotive ECUs. Target inference latency should be < 20-30ms for 100-message windows.
- **Multi-Layer Correlation:** Prioritize integration between CAN-level alerts and telematics anomalies to improve detection confidence and reduce false positives.
- **Validation Rigor:** Use temporal ordering for training/testing (train on earlier data, test on later). Implement cross-validation with time-series splits.

## Technical Architecture
### 1. CAN Bus Intrusion Detection (40%)
- **Parser:** Parse CAN frames (ID, DLC, Data, Timestamps).
- **Features:** 
    - Message-level: ID frequency, timing intervals, payload entropy.
    - Sequence: ID transition patterns, n-grams.
    - Statistical: Rolling statistics, deviations.
- **Models:** Random Forest, XGBoost, Isolation Forest, or One-Class SVM.
**Model development:**
     - train classifier for attack detection(supervised: RF, XGBoost)
     - implement anamoly detection baseline (unsupervised: isolation forest , one class SVM)
     - comapare the supervised vs unsupervised approches
     - evaluate per attack type performace(DoS vs Fuzzing vs Spoofing)
**Temporal analysis:**
    - implement windowed detection
    - analyse detection latency requirement for safety response



### 2. Telematics Behavioral Monitoring (30%)
- **Features:** Speed patterns, acceleration, braking intensity, trip frequency, location clusters.
- **Baseline Models:** Autoencoders or statistical profiles for defining "normal" behavior envelopes.

  - 

### 3. Multi-Layer Integration (15%)
- **Correlation:** Combine signals from CAN and telematics.
- **vSOC Alerts:** Design alerts mapped to MITRE ATT&CK for ICS/Automotive (e.g., T0855, T0843, T0830).

### 4. Deployment Constraints (15%)
- **Optimization:** Quantized NNs or lightweight decision trees.
- **Architecture:** Hybrid edge/cloud detection strategy.

## Deliverables Checklist
- [ ] Jupyter Notebook(s) with full pipeline (exploration to analysis).
- [ ] Trained & Serialized Models (pickle, joblib, or ONNX).
- [ ] Technical Report (3-5 pages).
- [ ] vSOC Alert Specification.

## Recommended Stack
- **Data:** pandas, numpy, scikit-learn.
- **CAN Parsing:** cantools, python-can.
- **ML:** xgboost, lightgbm, tensorflow-lite (optional).
- **Time-Series:** tsfresh, tslearn.
- **Profiling:** memory_profiler, timeit.

## References
- ISO/SAE 21434, UN R155/R156.
- MITRE ATT&CK for ICS.
- Car-Hacking Dataset (HCRL), SynCAN Dataset.
