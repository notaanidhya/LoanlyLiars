# Loan Performance Intelligence Engine — Data Dictionary

## 1. Overview
Plain-English field definitions for feature understanding, deterministic validation rules, and grounding the LLM Reviewer Copilot.

---

### 2. Primary Dataset Fields

| Field Name | Type | Description | Valid Values / Domain |
| :--- | :--- | :--- | :--- |
| `loan_id` | String | Unique loan sequence identifier | Freddie Mac loan ID (e.g. `F19Q10000056`) |
| `month_index` | Integer | Sequence index of the reporting cycle for this loan | `0, 1, 2, ...` |
| `reporting_month` | String | Monthly reporting period in YYYYMM format | `201902` to `202204` |
| `origination_month` | String | First scheduled payment month | `YYYYMM` (e.g. `201903`) |
| `loan_age_months` | Integer | Number of months elapsed since loan origination | `0` to `360` |
| `remaining_term_months` | Integer | Months remaining until legal loan maturity | `0` to `360` |
| `original_balance` | Float | Original unpaid principal balance (UPB) | `$10,000` to `$1,000,000` |
| `current_balance` | Float | Actual current unpaid principal balance | `$0.00` to `$1,000,000` |
| `interest_rate` | Float | Current note interest rate (percentage) | `2.0%` to `10.0%` |
| `credit_score_band` | Categorical | FICO credit score tier at origination | `<=620 (Poor)`, `621-680 (Fair)`, `681-740 (Good)`, `741-800 (Very Good)`, `801+ (Exceptional)` |
| `ltv_band` | Categorical | Loan-to-Value tier at origination | `<=60%`, `61-75%`, `76-80%`, `81-90%`, `91-95%`, `>95%` |
| `dti_band` | Categorical | Debt-to-Income tier at origination | `<=20%`, `21-30%`, `31-40%`, `41-45%`, `46-50%`, `>50%` |
| `state` | String | US State of mortgaged collateral | 2-letter state code (e.g. `CA`, `TX`, `NY`) |
| `loan_purpose` | Categorical | Loan origination purpose | `P` (Purchase), `C` (Cash-out Refi), `N` (No Cash-out Refi) |
| `occupancy_type` | Categorical | Occupancy status of property | `P` (Primary Residence), `S` (Second Home), `I` (Investment) |
| `property_type` | Categorical | Real estate property structure | `SF` (Single Family), `CO` (Condo), `PU` (PUD), `MH` (Manufactured) |
| `servicer_name` | String | Primary servicing institution | e.g. `Rocket Mortgage`, `Wells Fargo`, `Pennymac` |
| `current_status` | Categorical | Current monthly payment status | `CURRENT`, `30DPD`, `60DPD`, `90PLUS_DPD`, `DEFAULT`, `PREPAID` |
| `days_past_due` | Integer | Days delinquent on payment | `0, 30, 60, 90, 120, 180+` |
| `modification_flag` | String | Indicates loan restructuring/modification | `Y`, `N` |
| `prepayment_flag` | Integer | Binary indicator for full loan payoff | `0`, `1` |
| `default_flag` | Integer | Binary indicator for loan default/foreclosure | `0`, `1` |
| `loss_severity_band` | Categorical | Estimated loss severity tier upon default | `None`, `Low (10-25%)`, `Medium (26-45%)`, `High (46-70%)`, `Severe (>70%)` |
| `last_updated_at` | String | Timestamp of last system update | ISO 8601 UTC timestamp |
| `source_system` | String | Upstream origination/servicing feed | `CORE_SERVICING_SYSTEM` |
| `document_status` | Categorical | Loan file audit completeness | `VERIFIED`, `MISSING_NOTE`, `INCOMPLETE_INCOME`, `UNVERIFIED_APPRAISAL` |

---

### 3. Prediction Targets

| Target Field | Type | Horizon | Description |
| :--- | :--- | :--- | :--- |
| `next_3m_delinquency_flag` | Binary | 3 Months | 1 if loan becomes 30+ DPD within 3 months |
| `next_6m_delinquency_flag` | Binary | 6 Months | 1 if loan becomes 30+ DPD within 6 months |
| `next_12m_default_flag` | Binary | 12 Months | 1 if loan enters 90+ DPD or default within 12 months |
| `next_12m_prepayment_flag` | Binary | 12 Months | 1 if loan prepays in full within 12 months |
| `next_state` | Categorical | 1 Month | Status next month (`CURRENT`, `30DPD`, `60DPD`, `90PLUS_DPD`, `DEFAULT`, `PREPAID`) |
| `exception_required` | Binary | Instant | 1 if record contains data anomaly or conflict |
| `exception_type` | Categorical | Instant | `BALANCE_INCONSISTENCY`, `STATUS_CONFLICT`, `DOCUMENT_GAP`, `INVALID_TERM`, `SERVICER_CONFLICT`, `STALE_RECORD`, `NONE` |