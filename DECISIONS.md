# DECISIONS.md — Architectural Decision Log

Append-only. Each entry has a date, a status, the decision, the reason, and the alternatives that were considered and dropped. A superseded decision is marked as superseded, not deleted.

---

## ADR-001 — Split deterministic code and model judgment along the fixed constraint
**Date:** 2026-11-17 · **Status:** Accepted

**Decision.** Code owns: identity, entitlement, policy-in-force on the loss date, deductible, net payable, the total-loss threshold (repair > 70% of ACV), the adjuster authority limit ($15,000), and the injury-reported flag. The model owns: coverage interpretation against the clause wording and endorsements, narrative consistency across documents, fraud indicators, and the drafted reasoning. Each item in the response carries `source: "deterministic" | "model"`.

**Reason.** These operations have one correct answer, and getting them wrong is a regulatory or financial failure. A model can produce a plausible but wrong date comparison or subtraction. Labelling the source on each item makes acceptance criterion 3 (attribution within a response) checkable by a machine.

**Alternatives considered.**
- *Model computes everything, with code checking afterwards.* Dropped: it spends tokens on work with a known answer and makes the model's numbers look authoritative.
- *Extend the rule table to cover coverage and fraud.* Dropped: the brief notes that coverage depends on clause wording and fraud on narrative consistency, and neither can be encoded as rows.

---

## ADR-002 — Check entitlement in code, before any agent is invoked
**Date:** 2026-11-17 · **Status:** Accepted

**Decision.** Every route authenticates the caller, then checks `claim.assigned_adjuster == user OR user.role in {SUPERVISOR} AND claim.region in user.regions` against the CMS. A denied request returns `403` with no claim fields and writes an audit record, and no agent is constructed. Agent tools are bound to a single `claim_id` at construction, so an agent cannot fetch another claim.

**Reason.** Access control written as a model instruction can be talked around by prompt injection, and the rubric grades it Weak. Binding tools to one claim limits cross-record leakage by construction, rather than relying on the model to behave.

**Alternatives considered.**
- *System-prompt rule ("only discuss claims the user owns").* Dropped: not enforceable.
- *Check after retrieval, filter before responding.* Dropped: the data has already entered the model context, so it can leak through the reasoning.

---

## ADR-003 — Four decision outcomes; access refusal sits outside them
**Date:** 2026-11-18 · **Status:** Accepted (A4 in the charter: confirm against client codes)

**Decision.** Outcomes are `APPROVE` (covered, consistent, within authority), `DENY` (not in force, or a cited exclusion or condition applies), `REFER_SIU` (cited narrative inconsistency or fraud indicators), and `ESCALATE` (injury, probable total loss, above authority, missing required evidence, or ambiguous wording). `REFUSED` is an access result, not an outcome. Precedence when several apply: deterministic not-in-force `DENY` > `REFER_SIU` > `ESCALATE` > model `DENY` > `APPROVE`. Deterministic outcomes short-circuit the model and are labelled `source: "deterministic"`.

**Reason.** These match how adjusters already route work. A fixed order of precedence makes gold labels unambiguous. Fraud outranks escalation because an SIU referral must not get lost inside a total-loss or injury workflow.

**Alternatives considered.**
- *A free-text decision.* Dropped: it cannot be scored.
- *A single "refer" outcome for SIU and escalation together.* Dropped: SC-4 needs SIU routing to be measured on its own.

---

## ADR-004 — Read-only integration, apart from one idempotent draft write
**Date:** 2026-11-18 · **Status:** Accepted

**Decision.** The co-pilot reads from the CMS, PAS and DMS. Its only write is `PUT /claims/{id}/draft-decision`, keyed by `(claim_id, run_id)`, with status always `DRAFT_PENDING_ADJUSTER`. It never sets a final status or releases a payment, even if the requesting user asks it to.

**Reason.** A licensed adjuster must be accountable for every outcome. Retries must not create duplicate notes. A narrow write surface keeps the IT Integration Owner and CISO from blocking rollout.

**Alternatives considered.**
- *Auto-approve low-value, high-confidence claims.* Dropped: it conflicts with the brief and with Compliance. Recorded as a possible later phase, not in scope.

---

## ADR-005 — Citations must be verifiable against what was actually retrieved
**Date:** 2026-11-19 · **Status:** Accepted

**Decision.** Output is a strict typed schema enforced through Agents SDK structured output. Coverage citations are `clause_id` values, which must be a subset of the clause IDs returned by retrieval in that run. Evidence citations are `doc_id` plus an excerpt, which must appear in that document. A response that fails either check is not returned as a model verdict. It falls back to `ESCALATE` with `source: "deterministic_fallback"` and a reason.

**Reason.** An ungrounded citation is worse than none, because it looks authoritative. Checking citations against retrieval in code makes "cites retrieved clauses" demonstrable (rubric area C), and the fallback can be told apart from model output (Milestone 3, item 5).

**Alternatives considered.**
- *Ask the model to "only cite real clauses".* Dropped: a request the model can ignore, not a guarantee.

---

## ADR-006 — Gold labels come from reading the file, not from the legacy fraud score
**Date:** 2026-11-19 · **Status:** Accepted

**Decision.** Evaluation gold labels for `REFER_SIU` are set by reading the file for inconsistencies. The legacy score appears in the case as a field, and the suite deliberately includes high-score clean files and low-score inconsistent files. Document text is treated as untrusted. Instructions embedded in documents are adversarial inputs with their own cases.

**Reason.** The client's stated problem is score-threshold referral. If the labels followed the score, the system would be trained to reproduce the very behaviour we are replacing.

**Alternatives considered.**
- *Use historical SIU referrals as labels.* Dropped: they inherit the threshold bias, and in any case only synthetic data is allowed.
