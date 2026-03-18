# Technical Report: Multi-Layer Automotive Intrusion Detection System

## 1. Automotive Context & Problem Statement
Modern vehicles are increasingly connected, software-defined systems comprising dozens of Electronic Control Units (ECUs) communicating via the Controller Area Network (CAN). While CAN is the industry standard for its robustness and low cost, it lacks native security features such as authentication or encryption. 

With a reported 39% increase in automotive cyber incidents (2023–2024) and 85% of these attacks being remote, protecting the in-vehicle network is critical. Compromise of the CAN bus can lead to unauthorized control over safety-critical functions like braking, steering, and acceleration, posing a direct threat to passenger safety.

## 2. CAN Analysis & Feature Engineering
Our system targets three representative attack types from the HCRL dataset: **DoS, Fuzzy, and Spoofing (RPM/Gear)**. We utilized a **Consolidated Dataset** containing 250,000+ messages across these categories to ensure robust training.

### 2.1 Timing Analysis Visualization
The primary indicator of a message injection attack is the disruption of the network's natural timing.

![DoS Attack Timing](plots/timing_analysis.png)

**Interpretation:**
In the consolidated timing plot, we observe clear manifestations of different attack vectors:
- **DoS:** High-frequency injection (0.3ms) creates a dense horizontal band at the bottom.
- **Fuzzy:** Random CAN ID injections every 0.5ms disrupt the normal periodic flow.
- **Spoofing:** Targeted injections every 1.0ms specifically overwrite safety-critical RPM and Speed payloads.

## 3. Telematics Behavioral Modeling
The system derives vehicle speed and engine RPM proxies from CAN signals (IDs `043f` and `0316`) to define a "normal driving envelope."

### 3.1 Advanced Behavioral Profiling (Autoencoder)
In addition to the standard **3-Sigma Statistical Envelope**, we implemented an **Autoencoder (MLP-based)** to learn high-dimensional normal driving behavior. This model is specifically designed to capture the complex, non-linear relationships between vehicle state variables.

**Model Comparison:**
| Model | Approach | Advantage | Performance (Normal Data) |
| :--- | :--- | :--- | :--- |
| **3-Sigma** | Univariate Statistical | Low compute, high transparency. | 17 anomalies flagged |
| **Autoencoder** | Neural Reconstruction | Captures non-linear correlations. | **5 anomalies flagged** |

**Interpretation:**
By training an Autoencoder to reconstruct normal driving features (Speed, RPM, Acceleration), we identify anomalies by measuring **Reconstruction Error (MSE)**. The Autoencoder achieved a reconstruction threshold of **0.4590**. If an attack forces the RPM to 5000 while the Speed remains at 0 (a non-physical state), the Autoencoder generates a high error signal, triggering a behavioral alert. Its superior performance on normal data (fewer false positives) makes it ideal for multi-layer correlation.

## 4. Model Performance & Detection Accuracy
An **XGBoost Classifier** was trained on the consolidated multi-attack data and evaluated using a strict temporal split (80/20).

### 4.1 Multi-Attack Confusion Matrix
The confusion matrix demonstrates the model's ability to distinguish between Normal traffic and various injection vectors with extreme precision.

![Confusion Matrix](plots/confusion_matrix.png)

### 4.2 Key Performance Indicators (KPIs)
The following metrics were empirically validated during the model pipeline evaluation:

| Metric | Validated Value | Requirement | Status |
| :--- | :--- | :--- | :--- |
| **True Positive Rate (TPR)** | **99.38%** | > 95.0% | PASS |
| **False Positive Rate (FPR)** | **0.00%** | < 0.1% | PASS |
| **F1-Score** | **0.9969** | > 0.95.0 | PASS |
| **Inference Latency** | **6.10ms** | < 20.0ms | PASS |

**Analysis:**
The **0.00% False Positive Rate** is a critical achievement for automotive safety. In a real-world deployment, false positives can lead to "phantom braking" or unnecessary vehicle lockouts. Our model ensures that only genuine malicious injections are flagged for the correlation engine.

## 5. Multi-Layer Integration Strategy
The core innovation is the **Multi-Layer Correlation** engine. Alerts are categorized based on confidence:
1. **Critical (Confidence 2):** Overlapping CAN-level anomaly AND Behavioral deviation (e.g., Spoofing attack causing unphysical Speed/RPM correlation).
2. **Suspicious (Confidence 1):** Single-layer detection (e.g., a short DoS burst without behavioral impact).

All detections are mapped to the **MITRE ATT&CK for Automotive** taxonomy:
- **DoS:** T0855 (Unauthorized Command Message)
- **Fuzzy:** T0830 (Adversary-in-the-Middle)
- **Spoofing:** T0843 (Replay Attack)

## 6. Deployment Analysis
Resource profiling confirmed real-time feasibility on automotive hardware:
- **Throughput:** ~95,116 Messages Per Second (MPS) for XGBoost.
- **Resource Footprint:** 104.3 KB model size, making it suitable for edge ECU deployment.

## 7. Conclusions
The transition to a **Consolidated Multi-Attack Dataset** and the addition of **Neural Behavioral Modeling (Autoencoder)** has significantly increased the system's detection breadth. The multi-layer approach successfully filters transient network noise, ensuring that only safety-critical intrusions generate high-severity vSOC alerts with nearly zero false alarms.
