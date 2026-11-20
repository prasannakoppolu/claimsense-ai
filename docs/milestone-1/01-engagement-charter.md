# Engagement Charter — ClaimSense AI Claims Adjudication Co-pilot

| | |
|---|---|
| **Client** | Northwind Mutual Motor Insurance (fictional; synthetic engagement) |
| **Engagement** | 5 weeks, discovery → handover |
| **Forward deployed engineer** | _<your name>_ |
| **Executive sponsor / approver** | VP Claims Operations |
| **Charter version** | 1.0 — Week 1, 2026-11-19 |

## 1. Background

Northwind's motor adjusters handle every claim by hand. For each one, a single licensed adjuster pulls the claim from the claims management system, looks up the policy in the policy administration system, and opens every attachment in the document store. They then check coverage against the policy wording, form a view on fraud, total loss and injury exposure, and write the first decision. That decision varies from one adjuster to the next, its reasoning is not recorded, and fraud referral happens when a legacy score crosses a threshold, not when someone reads the file and finds the story doesn't hold together.

## 2. The real bottleneck

The client describes the problem as "decisions are slow". Discovery points to a narrower cause: **most of an adjuster's first-pass time goes on assembling the file and reconciling the narrative across documents**, not on making the decision itself. In practice that means switching between three systems, finding the clause that applies to this vehicle and this use, and checking that the FNOL, the police report, the repair estimate and the photos tell the same story.

Writing the decision is quick once the file is understood. Adding rows to the existing rule table cannot speed up file understanding, because:

- coverage depends on the **wording of a policy clause** and its endorsements, and
- fraud depends on **whether the narrative is consistent across documents**.

Both of these need reading, not lookup. Throughput is therefore governed by *gather + read + reconcile*. That is the stage the co-pilot targets, and it is what the latency and confirmation criteria measure.

> **To validate in Week 1:** a time-and-motion study of 20 recent claims, split into gather, read/reconcile, coverage check, risk assessment and write-up. Working hypothesis: gather + read/reconcile is at least 60% of first-pass time. If the study disproves this, the scope in §4 is revisited before Week 2 sign-off.

## 3. Objective

Cut an adjuster's first pass from hours to minutes. For every claim the user is entitled to see, the co-pilot returns:

1. a **first decision**: one of `APPROVE`, `DENY`, `REFER_SIU` or `ESCALATE`;
2. the **reasoning** for that decision;
3. **citations** to the evidence relied on: policy clause IDs that were actually retrieved, and document IDs with the relevant excerpt.

A **licensed adjuster confirms or overrides every outcome**. The co-pilot never finalises a claim or releases a payment.

## 4. Scope

**In scope**
- Read access to the three client systems through a participant-owned, authenticated service.
- Coverage assessment grounded in a searchable policy clause corpus.
- Narrative-consistency fraud assessment, plus total loss and injury exposure flags.
- Deterministic computation of policy-in-force status, deductible, net payable, total-loss threshold and adjuster authority limit.
- One write: a **draft** decision note on the claim, made idempotently.
- An audit record for every request, whether granted or refused.
- An evaluation suite with adversarial cases, gated in CI.

**Out of scope**
- Final settlement, payment release, or any customer communication.
- Third-party liability negotiation and injury valuation. Injury claims are routed to a specialist, not valued.
- Changing the client's legacy fraud score or rule table.
- Any production or personally identifiable data. **Synthetic data only, at every stage.**

## 5. Client systems and integration points

| # | System | System of record for | Integration point (co-pilot side) | Direction | Notes |
|---|---|---|---|---|---|
| 1 | **Claims Management System (CMS)** | Claim header: claim ID, loss date/time, loss type, location, assigned adjuster, status, reserve, legacy fraud score, prior claims | `GET /claims/{claim_id}`, `GET /claims?assigned_to={user}` | Read | The claim's assignment is the source of entitlement for access control. |
| | | Draft decision note | `PUT /claims/{claim_id}/draft-decision` | **Write** (only write in the system) | Idempotent on `(claim_id, run_id)`. Status is always `DRAFT_PENDING_ADJUSTER`. |
| 2 | **Policy Administration System (PAS)** | Policy schedule: inception/expiry, named drivers, vehicle, use class, deductibles, actual cash value, endorsements, policy wording version | `GET /policies/{policy_id}` | Read | Dates and money are computed from these fields **in code**. |
| | | Policy wording (clause text by ID) | Exported into the **policy clause corpus** for retrieval: `search(query, wording_version) → [{clause_id, text}]` | Read (batch export) | Coverage citations must be clause IDs returned by this search. |
| 3 | **Document Store (DMS)** | FNOL statement, police report, repair estimate, photos (with metadata), witness statements, medical notes, tow receipts | `GET /claims/{claim_id}/documents`, `GET /documents/{doc_id}` | Read | Document content is **untrusted input**. Embedded instructions are treated as data, never as commands. |

Every integration point sits behind the co-pilot's own authenticated service. The entitlement check runs in code **before** any agent is invoked, and agents only ever see data for the one claim the user is entitled to.

## 6. Fixed constraints

1. **Deterministic operations are implemented in code**: identity, access control, policy dates and monetary calculations.
2. **Judgment is delegated to a model and cited**: every judgment names the evidence it relied on.
3. **Synthetic data only.**

## 7. Success criteria (summary)

Full definitions, measurement method and dispute rules are in `03-success-criteria.md`.

| ID | Criterion | Target |
|---|---|---|
| SC-1 | Decision accuracy | ≥ 90% outcome match on held-out cases; 100% on safety-critical cases |
| SC-2 | Pipeline latency | p95 ≤ 60 s end to end; refusals p95 ≤ 1 s |
| SC-3 | Adjuster confirmation rate | ≥ 80% confirmed without outcome change; 0 outcomes finalised without an adjuster |
| SC-4 | Fraud routing accuracy | SIU recall ≥ 90%, precision ≥ 75% |

## 8. Timeline

| Week | Milestone | Exit evidence |
|---|---|---|
| 1 | Discovery and scoping | This charter, RACI, success criteria, `DECISIONS.md`, 20 eval cases |
| 2 | SoW, pricing, architecture | Signed SoW, architecture diagram, risk register, contracts, AWS resources |
| 3 | Production agents | Single-command stack; CI gate blocks the image push on a failing eval |
| 4 | Integration and access control | Authorised routes, two-user test, audit trail |
| 5 | Evaluation, observability, handover | 150-case suite, dashboard and alarm, incident drill, runbook, demo |

## 9. Assumptions and open questions

- **A1.** Adjuster authority limit is $15,000 net payable. Anything above it escalates. *(Confirm with the Claims Ops Manager.)*
- **A2.** The total-loss threshold is repair cost > 70% of actual cash value, per clause PM-3.2. *(Confirm the policy wording version.)*
- **A3.** Any reported bodily injury goes to an injury specialist, per PM-6.1.
- **A4.** The four decision outcomes below match the client's existing outcome codes. *(Confirm with the Claims QA Lead.)*
- **Q1.** Can the CMS accept a draft note without creating a workflow task? If not, the draft is written to the co-pilot's own store and linked from the CMS.
