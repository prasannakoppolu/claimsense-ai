# Stakeholder Map and RACI

## 1. Key roles at a glance

| Role required by the brief | Stakeholder | Why |
|---|---|---|
| **Approver** | VP Claims Operations (executive sponsor) | Owns the claims P&L and adjuster headcount. Signs the SoW and the go-live decision. |
| **Reviewer of co-pilot output** | Claims QA Lead (senior licensed adjuster) | Owns decision quality today. Labels the evaluation gold set and judges co-pilot drafts. |
| **Daily user** | Licensed Motor Adjusters | Run the co-pilot on assigned claims and confirm or override every outcome. |
| **Can block rollout** | CISO, Chief Compliance Officer, Head of SIU | Security (access, audit, data handling), regulatory duty (accountable licensed decisions, fair claims handling), and fraud referral policy. Each has a veto. |

## 2. Stakeholder map

| Stakeholder | Interest | Influence | Position (Week 1) | What they need from us | Engagement |
|---|---|---|---|---|---|
| VP Claims Operations | High | High | Sponsor | Shorter cycle time without added regulatory risk | Weekly steering update; go/no-go at Week 5 |
| Claims Operations Manager | High | High | Supportive, worried about adoption | Adjusters actually use it; authority limits respected | Co-designs the workflow; owns the runbook after handover |
| Claims QA Lead | High | Medium | Cautious | Reasoning she can audit; no rubber-stamping | Labels and freezes the gold set; reviews drafts weekly |
| Licensed Motor Adjusters | High | Medium | Mixed (fear of replacement) | Less swivel-chair work; final say stays theirs | Two adjusters in a pilot panel; feedback each week |
| Head of SIU | High | High (veto on fraud routing) | Sceptical of the score threshold | Fewer junk referrals; every referral states its reason | Reviews REFER_SIU cases; signs off SC-4 |
| CISO / InfoSec | Medium | High (veto) | Neutral | Authentication on every route, access check in code, full audit trail, synthetic data only | Architecture review in Week 2; access test evidence in Week 4 |
| Chief Compliance Officer | Medium | High (veto) | Neutral | A licensed adjuster accountable for every outcome; explainability | Reviews the human-in-the-loop design and audit fields |
| Legal / Procurement | Low | Medium | Neutral | IP and data handling terms | SoW review in Week 2 |
| IT Integration Owner (CMS/PAS/DMS) | Medium | Medium | Supportive if read-only | Read-only access, one idempotent write, no load spikes | Agrees the integration contracts in Week 2 |
| Model Risk / Data Science | Medium | Medium | Curious | Evaluation evidence, version pinning, rollback | Reviews the evaluation suite and CI gate |
| Forward Deployed Engineer | High | Medium | Delivery owner | Access, labelled cases, timely decisions | Runs all of the above |

**Power/interest summary**
- *Manage closely:* VP Claims Ops, Head of SIU, Claims Ops Manager.
- *Keep satisfied (veto holders):* CISO, Chief Compliance Officer.
- *Keep informed and involved:* QA Lead, adjusters, IT Integration Owner, Model Risk.
- *Monitor:* Legal / Procurement.

## 3. RACI

R = Responsible (does the work) · A = Accountable (one per row, signs off) · C = Consulted · I = Informed

| Activity / deliverable | VP Claims Ops | Claims Ops Mgr | Claims QA Lead | Adjusters | Head of SIU | CISO | Compliance | IT Integration | Model Risk | FDE |
|---|---|---|---|---|---|---|---|---|---|---|
| Engagement charter and scope | **A** | C | C | I | C | I | C | I | I | R |
| Success criteria and targets | **A** | C | C | C | C | I | C | I | C | R |
| Gold labels for evaluation cases | I | C | **A** / R | C | C (SIU cases) | I | I | I | C | R |
| SoW and pricing (Week 2) | **A** | C | I | I | I | C | C | C | I | R |
| Architecture and code/model boundary | I | C | C | I | C | C | C | C | C | **A** / R |
| System integration contracts | I | I | I | I | I | C | I | **A** | I | R |
| Access control and audit trail | I | C | I | I | I | **A** | C | C | I | R |
| Fraud routing behaviour (REFER_SIU) | I | C | C | I | **A** | I | C | I | C | R |
| Evaluation suite and CI gate | I | I | C | I | C | I | I | I | **A** | R |
| Confirming each co-pilot decision (in use) | I | I | C | **A** / R | I | I | I | I | I | I |
| Reviewing co-pilot output quality | I | C | **A** / R | C | C | I | C | I | C | R |
| Security sign-off for rollout | I | I | I | I | I | **A** / R | C | C | I | C |
| Regulatory sign-off for rollout | I | I | C | I | I | C | **A** / R | I | I | C |
| Go-live / rollout decision | **A** | R | C | I | C (veto) | C (veto) | C (veto) | C | C | C |
| Runbook and handover | I | **A** | I | I | I | C | I | C | I | R |

## 4. Escalation path

FDE → Claims Ops Manager → VP Claims Ops (within 2 working days). Any blocking concern from the CISO, Compliance or SIU goes straight to the VP Claims Ops and is logged in `DECISIONS.md`.
