# Loan Performance Intelligence Engine

An enterprise-grade, machine-learning-first system designed for comprehensive loan-data profiling, performance prediction, anomaly detection, scenario simulation, explainability, and grounded LLM-assisted review. 

Developed for the Intain Campus FinTech Challenge 2026 (AI Track), this platform moves beyond traditional API wrappers to deliver a rigorous, multi-faceted analytical engine for unstructured and tabular loan portfolios.

## System Architecture

The pipeline processes raw loan records through an advanced feature engineering layer before branching into multi-outcome supervised predictive models. The system arbitrates anomalies in real-time, extracts local feature attributions via TreeSHAP, and synthesizes these insights into an LLM-assisted reviewer copilot—all protected by deterministic hallucination guardrails.

```mermaid
graph TD
    classDef data fill:#2C3E50,stroke:#34495E,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef feature fill:#2980B9,stroke:#3498DB,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef model fill:#27AE60,stroke:#2ECC71,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef anomaly fill:#F39C12,stroke:#F1C40F,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef llm fill:#8E44AD,stroke:#9B59B6,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef safety fill:#C0392B,stroke:#E74C3C,stroke-width:2px,color:#FFF,rx:5px,ry:5px;
    classDef ui fill:#34495E,stroke:#2C3E50,stroke-width:2px,color:#FFF,rx:5px,ry:5px;

    RawData[Raw Loan Portfolios]:::data --> FE[Feature Engineering Pipeline]:::feature
    
    FE --> MP1[12M Default Prediction]:::model
    FE --> MP2[12M Prepayment Prediction]:::model
    FE --> MP3[3M Delinquency Prediction]:::model
    
    MP1 --> HA[Hybrid Anomaly Arbitrator]:::anomaly
    MP2 --> HA
    MP3 --> HA
    FE --> HA
    
    HA --> SHAP[TreeSHAP Explanations]:::model
    
    SHAP --> RC[LLM Reviewer Copilot]:::llm
    HA --> RC
    
    RC --> HAL[Hallucination Auditor Guardrail]:::safety
    
    HAL -- Validated Memo --> UI[Reviewer Action Dashboard]:::ui
    HAL -- Blocked Hallucination --> HAL_Fallback[Deterministic Override]:::safety
    HAL_Fallback --> UI
```

## Key Capabilities

* **Multi-Outcome Prediction:** Uses time-aware splits and calibrated supervised learning to forecast delinquency, default, prepayment probabilities, and state transitions.
* **Intelligent Data Profiling:** Automatically identifies distributions, missingness patterns, cross-column relationship breaks, and feature drift between training and production data.
* **Time-to-Event Modeling:** Includes survival analysis capabilities to approximate hazard and monthly transition outcomes.
* **Anomaly & Exception Detection:** Employs a hybrid arbitration engine generating record-level anomaly scores and prescriptive reviewer actions.
* **Stress Simulation Engine:** Executes macroeconomic stress scenarios (Base, Adverse-Credit, High-Prepayment) to project segment-level portfolio impacts.
* **Robust Explainability:** Integrates global feature importance and local TreeSHAP drivers to ensure complete transparency of model decisions.
* **Governed LLM Copilot:** Synthesizes model outputs and Shapley values into natural-language audit memos, constrained by strict hallucination auditor policies (HAL-001) that reject unsafe model recommendations.

## Quick Start

### Prerequisites
Ensure you have Python 3.10+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Live Demo
The project includes a terminal-based live demonstration script that performs sub-5-second inference, anomaly scoring, and grounded LLM generation across diverse test loans.

```bash
python demo.py
```

### Executing Pipeline Phases
The repository is structured logically into sequential phases for end-to-end retraining and evaluation:

1. **Phase 2:** Execute data intelligence and profiling.
   ```bash
   python run_phase2.py
   ```
2. **Phase 3:** Train predictive models and evaluate survival logic.
   ```bash
   python run_phase3.py
   ```
3. **Phase 4:** Run anomaly arbitration and SHAP explainability.
   ```bash
   python run_phase4.py
   ```
4. **Phase 5:** Run macroeconomic scenario stress tests.
   ```bash
   python run_phase5.py
   ```
5. **Phase 6:** Validate LLM Copilot and Hallucination Auditor.
   ```bash
   python run_phase6.py
   ```

## Repository Structure

* `src/`: Core logic modules.
  * `data/`: Automated feature engineering and data pipelines.
  * `models/`: Supervised model definitions and hybrid anomaly arbitration.
  * `llm/`: LLM reviewer copilot integration and hallucination auditor guardrails.
* `models/`: Pre-trained artifacts, calibrators, and feature encoders.
* `data/`: Data directory containing structured outputs and dictionary rules.
* `reports/`: Generated explainability reports, intelligence profiles, and scenario outputs.
* `submission/`: Final benchmark submission formats.

## License & Acknowledgments

Developed specifically for the Intain AI Track 2026. Code architecture and problem interpretations align with the official hackathon benchmark statements.
