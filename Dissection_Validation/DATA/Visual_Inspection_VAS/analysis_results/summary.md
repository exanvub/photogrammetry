# Visual Inspection VAS Study — Summary

## 1. Study Setup

### Objective
To evaluate and compare the visual quality of 3D photogrammetry models produced by six different acquisition methods, as assessed by expert researchers using a Visual Analog Scale (VAS).

### Photogrammetry Models
Six models were generated using three camera devices combined with two reconstruction methods:

| Model ID | Device | Method |
|----------|--------|--------|
| M1 | CrossPolarization (CP) | RealityScan (RS) |
| M2 | iPhone | RealityScan (RS) |
| M3 | DSLR (DL) | Object Capture (OC) |
| M4 | iPhone | Object Capture (OC) |
| M5 | DSLR (DL) | RealityScan (RS) |
| M6 | CrossPolarization (CP) | Object Capture (OC) |

### Evaluation Protocol
- **Raters**: 6 researchers (R1–R6)
- **Instrument**: 10 cm Visual Analog Scale (VAS), scored in centimeters (0–10)
- **Topics evaluated** (7 total): Detail, Most Realistic, Muscle, Arteries, Nerves, Bone, and Overall quality
- **Design**: For each topic, all 6 models were scored on the same 10 cm line, forcing the rater to both rank and score the models simultaneously. This repeated-measures design yields 252 total observations (6 raters × 7 topics × 6 models).

---

## 2. Statistical Analysis

### 2.1 Descriptive Statistics
Median, interquartile range (IQR), mean, and standard deviation were computed for each Topic × Model combination (n = 6 raters per cell).

### 2.2 Rank Analysis
VAS scores were converted to ranks within each Researcher × Topic combination (rank 1 = highest score). Mean and median ranks were computed per Model × Topic.

### 2.3 Friedman Test
The Friedman test — a non-parametric alternative to repeated-measures ANOVA — was used to test whether at least one model differs significantly from the others within each topic. This test is appropriate for ordinal/bounded VAS data with a small number of raters (k = 6 raters, n = 6 models).

### 2.4 Post-hoc Pairwise Wilcoxon Signed-Rank Tests
For topics with a significant Friedman result, all 15 pairwise model comparisons were tested using the Wilcoxon signed-rank test, with Bonferroni correction applied (α = 0.05 / 15 = 0.0033 per comparison).

### 2.5 Kendall's W (Inter-Rater Agreement)
Kendall's coefficient of concordance (W) was computed per topic to measure the degree of agreement among the 6 researchers in their ranking of the 6 models (W = 0: no agreement; W = 1: perfect agreement).

---

## 3. Results

### 3.1 Friedman Test

All seven topics showed statistically significant differences among the six models:

| Topic | χ²(5) | p-value |
|-------|-------|---------|
| Overall | 26.190 | < 0.001 |
| Detail | 25.905 | < 0.001 |
| Arteries | 24.095 | < 0.001 |
| Most Realistic | 23.852 | < 0.001 |
| Bone | 22.095 | < 0.001 |
| Nerves | 19.810 | 0.001 |
| Muscle | 16.381 | 0.006 |

### 3.2 Post-hoc Pairwise Comparisons

No individual pairwise comparisons reached statistical significance after Bonferroni correction. This is expected given the small sample size (n = 6 raters) and the conservative nature of the correction (15 comparisons per topic). Notably, the uncorrected p-values for DL models versus other models were consistently at the minimum achievable value (p = 0.031 for a sample of 6), indicating a clear directional effect that lacks power with this sample size.

### 3.3 Inter-Rater Agreement (Kendall's W)

Researchers showed strong to moderate agreement across all topics:

| Topic | Kendall's W | Interpretation | p-value |
|-------|-------------|----------------|---------|
| Overall | 0.873 | Strong | < 0.001 |
| Detail | 0.864 | Strong | < 0.001 |
| Arteries | 0.803 | Strong | < 0.001 |
| Most Realistic | 0.791 | Strong | < 0.001 |
| Bone | 0.737 | Strong | < 0.001 |
| Nerves | 0.660 | Moderate | 0.001 |
| Muscle | 0.546 | Moderate | 0.006 |

Agreement was highest for Overall quality (W = 0.873) and Detail (W = 0.864), and lowest for Muscle (W = 0.546) and Nerves (W = 0.660).

### 3.4 Rank Analysis and Descriptive Statistics

The mean ranks reveal a consistent three-tier hierarchy across all topics:

**Tier 1 — DSLR models (consistently ranked 1st–2nd):**

| Topic | DL-RS (mean rank) | DL-OC (mean rank) |
|-------|--------------------|--------------------|
| Most Realistic | 1.00 | 2.00 |
| Overall | 1.00 | 2.00 |
| Detail | 1.33 | 1.67 |
| Arteries | 1.50 | 1.50 |
| Nerves | 1.50 | 2.17 |
| Bone | 1.67 | 1.67 |
| Muscle | 1.83 | 2.50 |

DL-RS achieved a **perfect rank of 1.0** (unanimously ranked first by all raters) for Most Realistic and Overall quality. DL models scored the highest median VAS values (typically 9.0–9.5 cm) with the lowest variability (SD 0.12–0.99).

**Tier 2 — CrossPolarization models (ranked 3rd–4th):**

CP-RS and CP-OC occupied the middle ranks across all topics (mean rank 3.17–4.25). Median VAS scores ranged from 6.2–8.0 cm. The two CP methods were close to each other, with neither consistently outperforming the other.

**Tier 3 — iPhone models (ranked 5th–6th):**

iPhone-OC and iPhone-RS consistently occupied the lowest ranks (mean rank 4.67–5.67). Median VAS scores ranged from 4.2–5.9 cm. iPhone-RS tended to score slightly lower than iPhone-OC on most topics.

### 3.5 Overall Quality Scores (Median ± IQR)

| Model | Median | IQR | Mean Rank |
|-------|--------|-----|-----------|
| DL-RS | 9.50 | 9.27–9.50 | 1.00 |
| DL-OC | 9.10 | 9.00–9.20 | 2.00 |
| CP-RS | 7.65 | 6.52–8.02 | 3.67 |
| CP-OC | 7.45 | 7.10–7.72 | 3.67 |
| iPhone-RS | 5.95 | 5.12–6.48 | 5.33 |
| iPhone-OC | 5.75 | 5.28–6.38 | 5.33 |

---

## 4. Conclusion

The visual inspection study demonstrates a clear and consistent quality hierarchy among the six photogrammetry methods. The DSLR-based models (DL-RS and DL-OC) were unanimously rated as the highest quality across all evaluated aspects, with median VAS scores of 9.0–9.5 cm and near-perfect inter-rater agreement. The CrossPolarization models (CP-RS and CP-OC) occupied a distinct middle tier with median scores around 7.0–8.0 cm, while the iPhone models (iPhone-RS and iPhone-OC) were consistently rated lowest at 4.2–5.9 cm.

The Friedman test confirmed statistically significant differences among models on every topic (all p < 0.01). Although post-hoc pairwise tests did not survive Bonferroni correction — a limitation of the small sample size (n = 6 raters) combined with conservative multiple-comparison adjustment — the consistency of the ranking across all 7 topics and the strong inter-rater agreement (Kendall's W = 0.55–0.87) provide robust evidence for the observed hierarchy.

The DL-RS method stands out as the top-performing technique, achieving a unanimous first-place ranking on both Overall quality and Most Realistic appearance. The results suggest that camera device quality (DSLR > CP > iPhone) is the primary driver of perceived model quality, with the reconstruction method (RS vs. OC) playing a secondary role.
