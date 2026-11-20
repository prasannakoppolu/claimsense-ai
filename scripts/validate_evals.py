#!/usr/bin/env python3
"""Validate the evaluation case set before any model is involved.

Checks:
  - structure, unique IDs, and that all four decision outcomes are covered
  - required adversarial families are present
  - every expected clause citation exists in the policy clause corpus
  - every expected document citation exists in that case's fixtures
  - hand-set deterministic gold values match an independent recomputation
    (policy-in-force, deductible, net payable, total loss, authority limit)
  - reports the legacy score-threshold baseline for fraud routing (SC-4)

Exit code is non-zero on any failure, so this can run as a CI step.
Usage: python scripts/validate_evals.py [evals/cases.json] [evals/fixtures/policy_clauses.json]
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTCOMES = {"APPROVE", "DENY", "REFER_SIU", "ESCALATE"}
REQUIRED_ADVERSARIAL = {"prompt_injection", "cross_record_leakage", "forced_auto_decision", "unauthorized_access"}


def recompute(case, cfg):
    cl, pol = case["fixtures"]["claim"], case["fixtures"]["policy"]
    loss = datetime.fromisoformat(cl["loss_datetime"])
    in_force = datetime.fromisoformat(pol["inception"]) <= loss <= datetime.fromisoformat(pol["expiry"])
    ded = pol["deductibles"][cl["cover_section"]]
    acv, est = pol["vehicle"]["actual_cash_value"], cl["repair_estimate_total"]
    total_loss = est > cfg["total_loss_ratio"] * acv
    gross = acv if total_loss else est
    net = max(gross - ded, 0) if in_force else 0
    return {
        "policy_in_force": in_force,
        "deductible_applied": ded,
        "net_payable_if_covered": net,
        "total_loss": total_loss,
        "exceeds_authority": net > cfg["authority_limit"],
        "injury_flag": cl["injury_reported"],
    }


def main():
    cases_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evals/cases.json"
    corpus_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "evals/fixtures/policy_clauses.json"
    suite = json.loads(cases_path.read_text())
    clause_ids = {c["clause_id"] for c in json.loads(corpus_path.read_text())["clauses"]}
    cfg, cases = suite["config"], suite["cases"]
    errors = []

    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        errors.append("duplicate case IDs")

    outcomes, families = {}, {}
    for c in cases:
        e, cid = c["expected"], c["id"]
        families[c["family"]] = families.get(c["family"], 0) + 1
        if e.get("refused"):
            outcomes["REFUSED"] = outcomes.get("REFUSED", 0) + 1
            if e.get("outcome") is not None:
                errors.append(f"{cid}: refused case must have outcome null")
            if e.get("agent_invoked") is not False:
                errors.append(f"{cid}: refused case must assert agent_invoked=false")
            if not {"user", "action", "resource", "result"} <= set(e.get("audit", {})):
                errors.append(f"{cid}: refused case needs audit user/action/resource/result")
            continue
        o = e["outcome"]
        outcomes[o] = outcomes.get(o, 0) + 1
        if o not in OUTCOMES:
            errors.append(f"{cid}: unknown outcome {o}")
        if not e.get("requires_adjuster_confirmation"):
            errors.append(f"{cid}: every outcome must require adjuster confirmation")
        for cl in e["must_cite_clauses"]:
            if cl not in clause_ids:
                errors.append(f"{cid}: cites unknown clause {cl}")
        doc_ids = {d["doc_id"] for d in c["fixtures"]["documents"]}
        for d in e["must_cite_docs"]:
            if d not in doc_ids:
                errors.append(f"{cid}: cites unknown document {d}")
        if o == "REFER_SIU" and len(e["must_cite_docs"]) < 1:
            errors.append(f"{cid}: REFER_SIU must cite conflicting evidence")
        got = recompute(c, cfg)
        for k, v in e["deterministic"].items():
            if got[k] != v:
                errors.append(f"{cid}: deterministic {k} gold={v} recomputed={got[k]}")

    missing_outcomes = OUTCOMES - set(outcomes)
    if missing_outcomes:
        errors.append(f"outcomes not covered: {sorted(missing_outcomes)}")
    missing_adv = REQUIRED_ADVERSARIAL - set(families)
    if missing_adv:
        errors.append(f"adversarial families missing: {sorted(missing_adv)}")

    # Legacy score-threshold baseline for SC-4
    scored = [c for c in cases if not c["expected"].get("refused")]
    gold = {c["id"] for c in scored if c["expected"]["outcome"] == "REFER_SIU"}
    legacy = {c["id"] for c in scored
              if c["fixtures"]["claim"]["legacy_fraud_score"] >= cfg["legacy_referral_threshold"]}
    tp = len(gold & legacy)
    recall = tp / len(gold) if gold else 0
    precision = tp / len(legacy) if legacy else 0

    print(f"Cases: {len(cases)}  (adversarial: {sum(c['adversarial'] for c in cases)}, "
          f"holdout: {sum(c['split'] == 'holdout' for c in cases)})")
    print("Outcomes:", dict(sorted(outcomes.items())))
    print("Families:", dict(sorted(families.items())))
    print(f"Legacy threshold baseline (score >= {cfg['legacy_referral_threshold']}): "
          f"recall {recall:.0%}, precision {precision:.0%}  -> SC-4 target: recall >= 90%, precision >= 75%")
    if errors:
        print("\nFAIL")
        for err in errors:
            print("  -", err)
        sys.exit(1)
    print("\nPASS: case set is well-formed and deterministic gold values recompute correctly")


if __name__ == "__main__":
    main()
