# Technical Report: Multi-Layer Automotive Intrusion Detection System

## 1. Automotive Context & Problem Statement
Modern vehicles are increasingly connected, software-defined systems comprising dozens of Electronic Control Units (ECUs) communicating via the Controller Area Network (CAN). While CAN is the industry standard for its robustness and low cost, it lacks native security features such as authentication or encryption. 

With a reported 39% increase in automotive cyber incidents (2023–2024) and 85% of these attacks being remote, protecting the in-vehicle network is critical. Compromise of the CAN bus can lead to unauthorized control over safety-critical functions like braking, steering, and acceleration, posing a direct threat to passenger safety.

## 2. CAN Analysis & Feature Engineering
Our system targets three representative attack types from the HCRL dataset:
1. **DoS Attack:** Overloading the bus with high-priority '0000' CAN IDs.
2. **Fuzzy Attack:** Injecting random CAN IDs and data payloads to cause unpredictable behavior.
3. **Spoofing (RPM/Gear):** Injecting targeted messages to deceive the driver or specific ECUs.

### Feature Rationale
To detect these patterns, we implemented a multi-faceted feature extraction pipeline:
- **Timing Intervals (Delta T):** Detects high-frequency injection (DoS/Fuzzy) by identifying deviations from the expected message periodicity.
- **Payload Entropy:** Measures randomness in the 8-byte data field. Fuzzy attacks exhibit significantly higher entropy than normal messages.
- **N-gram Transitions:** Captures sequences of CAN IDs, identifying abnormal transitions typical of spoofing or unauthorized command injections.
- **Rolling Statistics:** Computes mean/standard deviation of timing to establish a dynamic baseline for network traffic.

## 3. Telematics Behavioral Modeling
In addition to network-level monitoring, the system implements telematics behavioral profiling. By deriving vehicle speed and engine RPM proxies from CAN signals (IDs `043f` and `0316`), we define a "normal driving envelope."

### Behavioral Baseline
We employed a **3-Sigma Statistical Envelope** approach. By learning the mean and standard deviation of acceleration profiles and braking intensity during normal operation, the system can flag deviations (e.g., sudden unintended acceleration or erratic RPM spikes) that correlate with CAN-level anomalies, significantly reducing false positives.

## 4. Detection Results & Performance
Our evaluation using the HCRL dataset yielded the following results for the **XGBoost-based IDS**:

| Attack Type | TPR (Detection) | FPR (False Alarm) | F1-Score |
| :--- | :---: | :---: | :---: |
| DoS Attack | 100.0% | 0.0% | 1.00 |
| Fuzzy Attack | 99.8% | 0.05% | 0.99 |
| Spoofing | 98.5% | 0.12% | 0.98 |

### Real-Time Efficiency
Inference latency was measured on a standard compute node to simulate automotive ECU performance:
- **Processing Time:** ~1.45ms per 100-message window.
- **Throughput:** >170,000 Messages Per Second (MPS).
- **Compliance:** Well within the mandated 20-30ms target, allowing for "line-rate" detection on a 500kbps-1Mbps CAN bus.

## 5. Multi-Layer Integration Strategy
The core innovation of this system is the **Multi-Layer Correlation** engine. Alerts are categorized into three tiers based on confidence:
1. **Informational:** Single-source anomaly (e.g., a one-off timing jitter).
2. **Suspicious:** Confirmed CAN-level attack pattern (e.g., DoS sequence detected).
3. **Critical:** Overlapping CAN-level attack AND telematics-level behavioral deviation (e.g., Gear spoofing combined with an erratic speed change).

This correlation is mapped to the **MITRE ATT&CK for Automotive** taxonomy, providing vSOC analysts with immediate context (e.g., T0855 for DoS or T0843 for Replay/Spoofing).

## 6. Deployment Analysis
We compared a "heavy" model (XGBoost) with a "lightweight" alternative (Shallow Decision Tree):

| Metric | XGBoost (Heavy) | Decision Tree (Light) |
| :--- | :---: | :---: |
| Serialized Size | 77.4 KB | 1.9 KB |
| Peak RAM | 48.1 KB | 166.4 KB |
| Throughput | 174,730 MPS | 332,003 MPS |

**Recommendation:** For high-performance gateways, XGBoost provides superior precision. For resource-constrained edge ECUs, the Decision Tree offers a highly efficient alternative with minimal footprint.

## 7. Limitations & Future Work
- **Aggressive Driving:** Sudden maneuvers may trigger false telematics anomalies. Future work should integrate driver-profile-specific baselines.
- **Mimicry Attacks:** Sophisticated attackers may inject messages at normal frequencies to evade timing-based detection. Sequence-based N-gram analysis is the primary defense here.
- **Encrypted CAN:** Future automotive architectures (CAN-XL) may use encryption, requiring the IDS to move from payload analysis to header/timing-only analysis.
