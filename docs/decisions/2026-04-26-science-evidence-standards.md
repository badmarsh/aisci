# Decision: Science Evidence Standards

Date: 2026-04-26

## Decision

Scientific claims in AiSci must be tracked through explicit evidence states:

- `Open` - claim identified but not checked.
- `Sanity checked` - local derivation or script supports the claim under stated assumptions.
- `Supported` - claim is tied to exact manuscript equations or tables, input data, reproducible outputs, and relevant literature.
- `Suggestive` - evidence points in a direction but does not establish causality or root cause.
- `Refuted` - evidence contradicts the claim.
- `Blocked` - missing data or manuscript detail prevents a decision.

## Rationale

The workspace combines RAG, coding agents, symbolic checks, and numerical fitting. These tools are useful, but they can make early results look more certain than they are. The project needs a durable distinction between local sanity checks and publication-grade scientific support.

## Consequences

- `research/robert/evidence-ledger.md` is the source of truth for claim status.
- Local scripts may print sanity-check results, but they should state assumptions and limits.
- Referee-style conclusions require full data, fit quality, covariance/correlation diagnostics, and literature-matched baselines.
- Archived brainstorming and legacy summaries should not be treated as current project status.
