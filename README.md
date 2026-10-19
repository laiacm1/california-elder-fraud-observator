# California Elder Fraud Observatory — Research Reproducibility

Independent data-science research by Laia Chandran-Moles. Public-facing project: [California Elder Fraud Observatory](https://www.caelderfraudobservatory.org/).

## What the project measures

This analysis uses California CDSS Adult Protective Services SOC 242 Item 19h / Cell 119, **financial-abuse investigation findings recorded at case closure**, across 58 California counties and six completed fiscal years (FY2019–20 through FY2024–25). The total includes different outcomes (confirmed, inconclusive and unfounded) involving **elders and younger dependent adults**. This is *not* a count of unique elder fraud victims, new monthly abuse reports, or the true prevalence of exploitation.

For descriptive normalization the study uses county age-65+ population figures. Because the outcome includes dependent adults under 65, normalized figures should **not** be interpreted as elder-only incidence rates. The project examines recorded APS findings, not incidents that never reach APS.

## Key findings and cautions

- 4,176 county-month entries: 2,901 exact counts, 1,195 suppressed cells, and 80 fully blank reports.
- The primary suppression-aware county trend model classified **34 increasing, 23 with no clear trend, and 1 decreasing** (under its original independence assumptions and multiple-testing adjustment). These classifications are model-dependent; some counties change under alternative suppression intervals and serial-dependence checks.
- Suppressed `*` cells are provisionally modeled as count intervals **1–10**, inferred from published zeros, smallest observed positive count 11, and confidentiality guidance. This is an inference, not formal CDSS verification of every suppressed cell. Fully blank entries are not imputed as zero.
- Recorded findings can change for reasons other than changes in actual exploitation, such as awareness, agency operations and case-closure timing. Direct county rankings as if they were abuse prevalence are inappropriate.

## Repository structure

- `data/source/`: public-study input tables as supplied for the October 2026 reproduction audit. Check the original CDSS/Census licensing and source documentation before redistribution elsewhere.
- `scripts/reproduce_trends.py`: reproduce county censored negative-binomial trend fits under 1–10 and hypothetical 0–11 suppression intervals.
- `scripts/run_reconciliation.py`: reconstruct pooled association model point estimates using five optimization starts.
- `results/verified/`: frozen *October audit* numerical outputs. The original August 14 exploratory trend classifications are intentionally **not** included here because their criteria differ.
- `docs/research_audit_2026-10-10.md`: detailed independent computational checks and outstanding limitations. **Read the follow-up correction at the end of the audit**: the pooled point estimates matched the final notebook after the correct benchmark was located.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/reproduce_trends.py
python scripts/run_reconciliation.py
```

Scripts create `*_recomputed.csv` next to the frozen verified result files. Results may vary modestly by optimizer/library versions. The full historical working notebook, its intermediate explorations, the 500-bootstrap verification notebook, and all website charts are **not** reproduced end-to-end by this repository release. See audit notes for limitations; this is a reproducible *core audit*, not a complete external certification.

## Reuse and maintenance

See the Observatory website for accessible explanations and source links. Research code and data version are a 2026 snapshot; the website and these files do not update automatically. No institutional affiliation or endorsement is implied. A software license has not yet been selected.
