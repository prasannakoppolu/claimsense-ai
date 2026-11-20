# ClaimSense AI — Claims Adjudication Co-pilot (Capstone)

A co-pilot that gives a licensed adjuster a first decision on a motor claim, with the reasoning and cited evidence, in minutes. Deterministic operations (identity, access, dates, money) run in code. Judgment runs in a model and is always cited. Data is synthetic only.

## Milestone 1 — Discovery and scoping
| # | Deliverable | Location |
|---|---|---|
| 1 | Engagement charter (three systems and integration points) | [`docs/milestone-1/01-engagement-charter.md`](docs/milestone-1/01-engagement-charter.md) |
| 2 | Stakeholder map and RACI | [`docs/milestone-1/02-stakeholders-raci.md`](docs/milestone-1/02-stakeholders-raci.md) |
| 3 | Four quantified success criteria | [`docs/milestone-1/03-success-criteria.md`](docs/milestone-1/03-success-criteria.md) |
| 4 | Architectural decision log (6 dated decisions) | [`DECISIONS.md`](DECISIONS.md) |
| 5 | 20 evaluation cases covering all four outcomes, 7 adversarial | [`evals/`](evals/README.md) |

Validate the case set (Python 3.12+, standard library only):
```
python scripts/validate_evals.py
```
