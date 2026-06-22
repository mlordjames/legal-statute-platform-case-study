# Technical Decisions

Short decision records explaining key engineering choices. Sanitized — no production
implementation details are exposed.

## 1. State-by-state extraction architecture

**Decision:** Build extraction as independent, per-state units rather than one monolithic crawler.
**Why:** Each state publishes legal material differently. Isolating states keeps one source's quirks
from breaking others, lets work proceed in parallel, and makes coverage easy to report and scale
incrementally toward all 50 states.

## 2. Checkpoint / resume

**Decision:** Persist progress checkpoints during long extraction and enrichment runs.
**Why:** State-level runs are long and can be interrupted (network, rate limits, restarts).
Checkpointing lets a run resume from the last good point instead of restarting, saving time and
LLM/compute cost.

## 3. Bulk CourtListener data instead of slow API crawling

**Decision:** Use CourtListener **bulk data** for case law rather than crawling their API
record-by-record.
**Why:** Bulk downloads are dramatically faster and gentler than per-record API calls for hundreds
of thousands of cases. Bulk-first ingestion plus columnar storage scales far better than API-only
crawling.

## 4. Parquet for case-law analytics

**Decision:** Store case-law datasets as Parquet.
**Why:** Parquet's columnar format gives strong compression and fast, selective scans — ideal for
analytical queries over 500k+ records where only a few columns are read at a time.

## 5. AWS S3 + Athena-style design

**Decision:** Use S3 as the storage backbone with an Athena-compatible SQL layer.
**Why:** S3 + Athena is a serverless lakehouse pattern: cheap durable storage, no cluster to manage,
and standard SQL over Parquet. It scales with data volume without re-architecting.

## 6. Separating extraction from enrichment

**Decision:** Keep extraction and AI enrichment as distinct stages with a validated record in
between.
**Why:** Extraction and enrichment fail for different reasons and have very different costs.
Decoupling them means re-extracting a source never forces re-enrichment, and enrichment can be
re-run or improved independently.

## 7. Validation checks before enrichment

**Decision:** Run data-quality validation before any record is enriched or stored.
**Why:** Enriching bad input wastes LLM cost and pollutes analytics. Validating first ensures only
clean, well-formed records reach enrichment and storage.

## 8. Keep the production repo private, publish a sanitized case study

**Decision:** Keep the client's production repository and dataset private; publish this sanitized
case study separately.
**Why:** Client confidentiality. The public artifact communicates the architecture, decisions, and
impact without exposing production code, data, credentials, prompts, or client identity.

## 9. Publish both a PDF case study and a sanitized GitHub repo for Fiverr Pro

**Decision:** Provide a polished PDF *and* a public GitHub repo.
**Why:** Reviewers skim differently — the PDF gives a fast, professional overview, while the repo
lets technically-minded reviewers inspect the architecture, diagrams, and sample schemas in depth.
