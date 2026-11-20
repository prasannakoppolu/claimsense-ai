# Success Criteria

These four criteria are written so that anyone holding the submitted commit can later settle the question "did the engagement work?" by running something, not by arguing. Each criterion fixes **what is measured, on what data, how, and what counts as a pass**.

## Shared definitions

- **Outcome**: one of `APPROVE`, `DENY`, `REFER_SIU`, `ESCALATE` (see `DECISIONS.md`, ADR-003). An access refusal (`REFUSED`) is not an outcome and is scored separately.
- **Gold label**: the expected outcome for a case. It is set by the Claims QA Lead (and the Head of SIU for fraud cases), recorded in `evals/cases.json`, and frozen by git commit.
- **Held-out set**: cases tagged `"split": "holdout"`. They are not used when writing prompts or tuning. By Week 5 at least 50 of the 150 cases are held out.
- **Safety-critical set**: deterministic denials (policy not in force), access refusals, forced auto-decision cases, and cross-record leakage cases.
- **Measurement run**: the evaluation suite runs on the tagged commit with the pinned model version, **3 times**. **The worst of the 3 runs is the score.**
- **Gold-label changes** after freeze need a dated `DECISIONS.md` entry approved by the Claims QA Lead. Changes made after a measurement run do not count towards that run.

---

## SC-1 Decision accuracy

| | |
|---|---|
| **Metric** | Share of held-out cases where the co-pilot's outcome equals the gold outcome |
| **Target** | **≥ 90%** on the held-out set **and 100%** on the safety-critical set |
| **Also required** | 100% of cited clause IDs appear in that run's retrieval results. A case with an ungrounded citation is scored **incorrect** even if its outcome matches. |
| **Data** | `evals/cases.json`, held-out and safety-critical splits |
| **Method** | `make eval` in CI on the tagged commit; 3 runs; worst run counts |
| **Baseline** | Agreement between two adjusters on the same files. To be measured in Week 1 by double-labelling 20 cases; hypothesis 75–85%. |

## SC-2 Pipeline latency

| | |
|---|---|
| **Metric** | Wall-clock time from the authorised request reaching the API to the complete decision payload being returned |
| **Target** | **p95 ≤ 60 s**, p50 ≤ 25 s, for granted requests. **p95 ≤ 1 s** for refused requests (no agent invoked). |
| **Data** | ≥ 100 requests replaying the evaluation cases against the **deployed AWS environment**, at a concurrency of 5 |
| **Method** | Server-side timings from the observability stack (not client timings); reported on the Week 5 dashboard |
| **Excludes** | Adjuster review time, which is tracked under SC-3 |
| **Baseline** | Manual first pass. Hypothesis 60–120 min per claim, confirmed by the time-and-motion study in the charter (§2). |

## SC-3 Adjuster confirmation rate

| | |
|---|---|
| **Metric** | Share of co-pilot first decisions that the reviewing licensed adjuster **confirms without changing the outcome** |
| **Target** | **≥ 80%** |
| **Hard constraint** | **0** outcomes finalised without a recorded adjuster confirmation (user ID, timestamp, confirm/override) |
| **Anti-rubber-stamp guard** | Median review time ≥ 2 min per claim, **and** ≥ 1 seeded wrong draft per 20 reviews must be caught. If the guard fails, the rate does not count. |
| **Data** | Capstone: a panel of 2 reviewers on 50 held-out cases, with 3 seeded wrong drafts. Pilot: first 200 live claims or 4 weeks, whichever comes first. |
| **Method** | Confirmation events read from the audit trail |

## SC-4 Fraud routing accuracy

| | |
|---|---|
| **Metric** | Over all cases, treating `REFER_SIU` as the positive class: **recall** = SIU-gold cases routed to SIU ÷ all SIU-gold cases; **precision** = SIU-gold cases routed to SIU ÷ all cases routed to SIU |
| **Target** | **Recall ≥ 90%** and **precision ≥ 75%** |
| **Also required** | 100% of `REFER_SIU` outputs cite at least two conflicting pieces of evidence (document IDs with excerpts). A referral without them is scored as a false positive. |
| **Reference comparison** | The legacy score threshold (score ≥ 70 → refer) is scored on the same cases. The co-pilot must beat it on **both** recall and precision. The set deliberately includes high-score clean files and low-score inconsistent files. |
| **Data** | Every case in `evals/cases.json`; at least 20% of the Week 5 suite is SIU-gold |
| **Sign-off** | Head of SIU |

---

## Summary

| ID | Criterion | Target | Measured on | Owner |
|---|---|---|---|---|
| SC-1 | Decision accuracy | ≥ 90% held-out; 100% safety-critical; 100% grounded citations | Eval suite, worst of 3 runs | Claims QA Lead |
| SC-2 | Pipeline latency | p95 ≤ 60 s granted; p95 ≤ 1 s refused | Deployed AWS, ≥ 100 requests | FDE / IT |
| SC-3 | Adjuster confirmation | ≥ 80% unchanged; 0 unconfirmed finals | Reviewer panel / pilot audit trail | Claims Ops Mgr |
| SC-4 | Fraud routing | Recall ≥ 90%, precision ≥ 75%; beats legacy threshold | Eval suite | Head of SIU |
