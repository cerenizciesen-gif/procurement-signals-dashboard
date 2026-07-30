# Justification of the technology choice

Appendix to the management paper. The assignment names AWS as the central implementation
option and permits alternatives "provided the choice is justified". This document provides
that justification and shows that the chosen implementation is architecturally equivalent.

## Decision

The prototype does not run on AWS. It runs on a GitHub repository, using GitHub Actions for
scheduling and GitHub Pages for hosting.

Reasons:

1. **Course instruction.** For this project AWS was explicitly waived and a direct
   implementation via GitHub was recommended.
2. **Project situation.** The group is reduced to one person; the available time goes into
   domain logic and the data model rather than cloud configuration.
3. **Operating model.** The Learner Lab stops every session after four hours. A monitoring
   tool that the concept defines as continuous and running daily is therefore not
   permanently reachable there. GitHub Actions runs the job on a schedule and GitHub Pages
   serves the dashboard permanently.
4. **Traceability.** Every run, every version of the data and every code change is recorded
   as a commit. For the required reproducible documentation this is an advantage over a
   manually configured sandbox whose state cannot be versioned.

## Architectural equivalence

Every component of the AWS reference setup has a counterpart in the implemented solution.
The architecture is the same; only the runtime environment differs.

| Function | AWS variant | Implementation in this project |
| --- | --- | --- |
| Knowledge store | S3 bucket holding `wissen.json` | `procurement_dataset.csv` in the repository |
| Processing logic | Lambda function | `analyze_data.py` |
| Orchestration, scheduling | Step Functions, EventBridge | GitHub Actions, cron daily at 05:00 UTC |
| Model access | API key in the Lambda environment | `ANTHROPIC_API_KEY` as a repository secret |
| Result interface | Lambda function URL | `signals.json` in the repository |
| Frontend hosting | Amplify | GitHub Pages |
| Access control | IAM, LabRole | Repository permissions, secrets management |

## The retrieval-augmented generation principle

The course material defines three criteria for a working RAG foundation. All three are met:

| Criterion | Evidence |
| --- | --- |
| **Retrieval** — the function actively fetches knowledge from an external source | `analyze_data.py` reads the price series, volumes and macro risks from `procurement_dataset.csv` |
| **Generation** — the answer is produced on the basis of that external data | The negotiation argument is built solely from the previously computed figures; the prompt contains no other facts |
| **Separation of knowledge and model** | The content sits in the data file, not in the code and not in the model |

The implementation goes beyond the reference setup in one respect: calculation, decision rule
and text generation are separated. All monetary figures and indicators are computed in
Python, the buy-or-wait signal follows an inspectable rule table, and the language model only
phrases the argument. The model is never asked to calculate, forecast or decide, so a
hallucinated figure cannot reach the recommendation. Details in `prompts.md`.

## Current state of the generative layer

The generative components are implemented and documented, but no API key is configured. The
system therefore runs on non-model fallbacks — keyword rules for screening, the rule sentence
for the argument — and the dashboard labels both states openly rather than presenting rule
output as model output.

Two consequences are deliberate:

- A scheduled run without a working key does **not** overwrite an argument that was genuinely
  generated earlier. Replacing a real completion with the weaker rule sentence would degrade
  the output silently.
- Supplying a key is the only change needed to activate the generative path. No code or
  configuration change is required.

## External source monitoring

The concept promised news and industry monitoring. `monitor_sources.py` implements it against
two public sources, neither of which needs a credential:

| Source | What it provides | How it is processed |
| --- | --- | --- |
| Turkish central bank daily reference rate | USD/TRY today and roughly thirty days back | The change is computed in code and flagged as a risk above a fixed threshold |
| Public news search feed | Headlines for freight, wage, supply and sanction topics | Classified into the risk taxonomy by a language model, or by keyword rules without a key |

Two design decisions are worth defending:

1. **The monitor does not decide.** Its findings are written to a separate file and attached
   to the output for display. They only drive the recommendation when `USE_LIVE_MACRO` is set.
   The default is off, so the test plan runs against the deterministic mockup dataset and its
   expected values remain valid. Live inputs and test fixtures are kept apart deliberately.
2. **The taxonomy is closed.** The classifier may only return one of three known risk factors.
   Anything else is discarded in code. A monitor that could invent categories would produce
   findings the decision logic cannot act on.

A source that cannot be reached is recorded as unavailable and the run continues. The
monitoring step is also marked `continue-on-error` in the workflow, so an outage in an
external feed can never block the signal generation that follows it.

## What is given up by not using AWS

Stated openly so the limits of the implementation are clear:

- **No vector index.** Retrieval is a file read that passes the relevant rows in full, not a
  semantic search over a knowledge base. At the data volume in question — three materials,
  twelve months — a vector index is not functionally necessary.
- **No historical archive of detected events.** Each monitoring run overwrites the previous
  findings. Trend analysis over detected risks would need a stored history.
- **No scaling to many concurrent users.** The dashboard is a static page reading a
  pre-computed file. Sufficient for pilot operation, not for production use with role-based
  permissions.
- **No role-based access control.** The non-functional requirement for a role model from the
  concept is not implemented in the prototype and remains a recommendation for further
  development.

## Recommendation for further development

The architecture is arranged so that moving to AWS would not require redevelopment:
`analyze_data.py` becomes the Lambda function, the data file moves into an S3 bucket, the
cron trigger becomes EventBridge, the dashboard moves to Amplify. The domain logic stays
unchanged. Such a move is recommended once live market data is connected and a role model
becomes necessary.
