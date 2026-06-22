# Sanitization Notes

This repository is a deliberately sanitized public case study. The following were **excluded** from
this repo to protect client confidentiality and security:

- **Full production source code** — only architecture summaries and small illustrative scripts are
  included.
- **Full datasets** — no production statute or case-law datasets; only synthetic sample records.
- **`raw_text`** — full raw statute/case text is never included; only short sanitized previews.
- **API keys, tokens, and secrets** — none are present in this repo.
- **`.env` files** — excluded and gitignored.
- **Client details** — the client is referenced only as a *confidential legal tech client*; no
  client name, branding, or identifying information appears.
- **Private prompts** — internal enrichment/tagging prompts are not included.
- **Production configs** — no production configuration, infrastructure state, or deployment settings.
- **Exact scraper logic** — production extraction implementation details are summarized, not exposed.
- **Confidential reports** — internal client reports and outputs are excluded.
- **Private command logs** — shell/command history and run logs are excluded.
- **Internal file paths** — internal directory structures and absolute paths are not exposed.

## What *is* included

- Anonymized architecture and data-model documentation.
- Synthetic, clearly-labeled sample records.
- Mermaid diagrams recreated at a safe, high level.
- A chart-generation script that runs only on the sanitized aggregate metrics.
- A polished PDF case study built from the same sanitized content.

## Verification

A secrets/PII sweep was run over this repository before commit, checking for API keys, tokens,
passwords, `raw_text`, provider names, AWS credentials, and any client name. The `.gitignore`
additionally blocks `.env` files, data formats (`*.parquet`, `*.csv`, `*.zip`, etc.), local virtual
environments, and internal scratch directories from ever being committed.
