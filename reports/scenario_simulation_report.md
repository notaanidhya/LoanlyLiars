# Macroeconomic Scenario & Stress Simulation Report

**Intain AI Track 2026 — Phase 5: Scenario Simulation & Capital Stress Engine**  

---

## 1. Executive Summary & Macroeconomic Findings

This report evaluates the portfolio under three governing macroeconomic trajectories specified in `macro_scenarios.csv`:
1. **Base Case**: Stable interest rates, moderate HPA (+2.5%), and baseline hazard curves ($1.0\times$).
2. **Adverse Credit**: +150 bps rate shock, +3.5% unemployment shock, -10% home price contraction, scaling default hazards by **2.30x** and compressing prepayment to **0.65x**.
3. **High Prepayment**: -150 bps rate shock driving refinancing velocity, scaling prepayment hazards by **2.75x** and lowering default hazards to **0.85x**.

### 12-Month Multi-Scenario Capital Impact Summary

| Macro Scenario | 12M Default Rate | 12M Prepay Rate | Performing Balance ($) | Defaulted Balance ($) | Loss at Risk (35% Sev) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **`Base`** | 1.27% | 61.21% | $5,953,062,798 | $201,502,925 | **$70,526,024** |
| **`Adverse_Credit`** | 7.25% | 52.79% | $6,340,202,276 | $1,150,311,975 | **$402,609,191** |
| **`High_Prepayment`** | 0.24% | 76.17% | $3,742,877,169 | $38,079,293 | **$13,327,753** |

---

## 2. Multi-Horizon Competing Hazard Curves

![Scenario Hazard Trajectories](figures/scenario_hazard_curves.png)

> **Figure 1 Insight**: In the *Adverse Credit* scenario, the dual impact of rate hikes and LTV degradation shifts the 36-month cumulative default rate significantly upward, while the *High Prepayment* scenario accelerates capital return, shrinking active performing balances within 18 months.

### Comprehensive Horizon Projections (3M to 36M)

| Scenario | Horizon | Cum. Default % | Cum. Prepay % | Delinquency % | Loss at Risk ($) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Base` | 3M | 0.39% | 22.41% | 3.30% | $21,657,598 |
| `Base` | 6M | 0.71% | 38.75% | 3.34% | $39,427,935 |
| `Base` | 12M | 1.27% | 61.21% | 3.43% | $70,526,024 |
| `Base` | 18M | 1.79% | 75.15% | 3.51% | $99,402,821 |
| `Base` | 24M | 2.28% | 83.95% | 3.59% | $126,613,649 |
| `Base` | 36M | 3.20% | 93.21% | 3.75% | $177,703,367 |
| `Adverse_Credit` | 3M | 2.29% | 18.22% | 5.75% | $127,168,972 |
| `Adverse_Credit` | 6M | 4.09% | 32.19% | 5.82% | $227,127,116 |
| `Adverse_Credit` | 12M | 7.25% | 52.79% | 5.96% | $402,609,191 |
| `Adverse_Credit` | 18M | 10.08% | 66.82% | 6.10% | $559,765,606 |
| `Adverse_Credit` | 24M | 12.68% | 76.54% | 6.24% | $704,149,592 |
| `Adverse_Credit` | 36M | 16.17% | 81.83% | 6.53% | $897,957,327 |
| `High_Prepayment` | 3M | 0.07% | 31.90% | 2.35% | $3,887,261 |
| `High_Prepayment` | 6M | 0.13% | 52.40% | 2.37% | $7,219,199 |
| `High_Prepayment` | 12M | 0.24% | 76.17% | 2.43% | $13,327,753 |
| `High_Prepayment` | 18M | 0.34% | 87.85% | 2.49% | $18,880,983 |
| `High_Prepayment` | 24M | 0.43% | 93.74% | 2.55% | $23,878,890 |
| `High_Prepayment` | 36M | 0.60% | 97.40% | 2.66% | $33,319,381 |

---

## 3. Markov State Roll-Rate Migration

![Markov State Migration](figures/transition_stress_comparison.png)

> **Figure 2 Insight**: The 24-month Markov chain dynamics reveal significant divergence in state occupancy. Under *Adverse Credit*, the 30-day and 60-day delinquency states experience a surge due to cure-rate compression, driving a steady accumulation into the terminal 90+ DPD default bucket.

---

## 4. Segment-Level Stress Vulnerability Analysis

![Segment Stress](figures/segment_stress_heatmap.png)

### High-Risk Credit & Geography Segment Breakdown

| Dimension | Segment Band | Loans | Portfolio Share | Base 12M Def% | Adverse 12M Def% | Stress $\Delta$ | Adverse Loss ($) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `credit_score_band` | **681-740 (Good)** | 28,378 | 32.1% | 1.96% | **8.75%** | +6.79% | **$155,970,468** |
| `ltv_band` | **91-95%** | 13,996 | 18.6% | 2.94% | **12.86%** | +9.91% | **$132,636,007** |
| `credit_score_band` | **741-800 (Very Good)** | 40,784 | 45.0% | 0.43% | **4.12%** | +3.68% | **$102,784,376** |
| `ltv_band` | **76-80%** | 22,060 | 24.1% | 1.50% | **7.36%** | +5.86% | **$98,544,511** |
| `servicer_name` | **Nationstar Mortgage LLC (Mr. Cooper)** | 11,448 | 12.2% | 2.03% | **10.05%** | +8.02% | **$67,972,738** |
| `ltv_band` | **81-90%** | 9,802 | 12.7% | 0.94% | **7.99%** | +7.05% | **$56,365,537** |
| `servicer_name` | **U.S. Bank National Association** | 11,780 | 12.6% | 1.98% | **8.39%** | +6.41% | **$58,456,655** |
| `state` | **NY** | 4,516 | 6.0% | 1.41% | **14.65%** | +13.24% | **$48,533,848** |
| `servicer_name` | **Rocket Mortgage, LLC** | 11,240 | 12.4% | 1.61% | **7.35%** | +5.74% | **$50,827,513** |
| `ltv_band` | **61-75%** | 21,771 | 22.4% | 0.90% | **3.96%** | +3.06% | **$49,178,839** |
| `servicer_name` | **Newrez LLC** | 11,605 | 11.7% | 0.96% | **6.05%** | +5.09% | **$39,484,452** |
| `servicer_name` | **Wells Fargo Bank, N.A.** | 11,456 | 12.9% | 0.85% | **4.97%** | +4.12% | **$35,640,674** |
| `credit_score_band` | **621-680 (Fair)** | 12,280 | 12.1% | 2.47% | **6.70%** | +4.23% | **$44,936,955** |
| `servicer_name` | **Pennymac Loan Services, LLC** | 11,822 | 13.3% | 1.39% | **5.13%** | +3.74% | **$37,796,740** |
| `state` | **NJ** | 2,655 | 3.0% | 3.86% | **20.12%** | +16.27% | **$33,677,527** |

---

*Report generated by Intain AI Track — Phase 5: Macro Scenario & Stress Simulation Engine*
